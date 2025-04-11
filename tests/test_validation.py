# tests/test_validation.py
import pytest
import json
import shutil
import hashlib
import zipfile
from pathlib import Path
import os

from src.tools.validate_oasf import validate_oasf

@pytest.fixture
def valid_oasf_path(tmp_path):
    """Fixture que crea un archivo .oasf válido temporal"""
    # Estructura de directorios
    oasf_dir = tmp_path / "demo_valid"
    (oasf_dir / "tracks/audio").mkdir(parents=True)
    (oasf_dir / "tracks/midi").mkdir(parents=True)
    
    # Archivos dummy
    audio_data = b"dummy_audio_data"
    midi_data = b"dummy_midi_data"
    
    (oasf_dir / "tracks/audio/snare.wav").write_bytes(audio_data)
    (oasf_dir / "tracks/midi/bassline.mid").write_bytes(midi_data)
    
    # Hashes reales
    audio_hash = "sha3-512:" + hashlib.sha3_512(audio_data).hexdigest()
    midi_hash = "sha3-512:" + hashlib.sha3_512(midi_data).hexdigest()
    
    # MANIFEST.json
    manifest = {
        "version": "1.0",
        "bpm": 120,
        "author": "Test User",
        "audio_tracks": [
            {
                "id": 1,
                "name": "Snare Drum",
                "path": "tracks/audio/snare.wav",
                "hash": audio_hash
            }
        ],
        "midi_tracks": [
            {
                "id": 2,
                "name": "Bassline",
                "path": "tracks/midi/bassline.mid",
                "hash": midi_hash
            }
        ]
    }
    (oasf_dir / "MANIFEST.json").write_text(json.dumps(manifest, indent=2))
    
    # Comprimir
    shutil.make_archive(str(tmp_path / "demo_valid"), 'zip', oasf_dir)
    return str(tmp_path / "demo_valid.zip")

def modify_zip_file(zip_path, modify_func):
    """Modifica un archivo ZIP sin causar warnings de duplicados"""
    temp_dir = Path(zip_path).parent / "temp_zip"
    temp_dir.mkdir(exist_ok=True)
    
    try:
        # Extraer todo el contenido
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(temp_dir)
        
        # Modificar el contenido
        modify_func(temp_dir)
        
        # Recrear el ZIP completamente nuevo
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = str(file_path.relative_to(temp_dir))
                    zipf.write(file_path, arcname)
    finally:
        shutil.rmtree(temp_dir)

def test_valid_oasf(valid_oasf_path):
    """Prueba con archivo válido"""
    assert validate_oasf(valid_oasf_path) is True

def test_invalid_hash(valid_oasf_path, tmp_path):
    """Prueba con hash inválido"""
    invalid_path = str(tmp_path / "demo_invalid.zip")
    shutil.copy(valid_oasf_path, invalid_path)
    
    def modify_manifest(temp_dir):
        manifest_path = temp_dir / "MANIFEST.json"
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        manifest["audio_tracks"][0]["hash"] = "sha3-512:00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000"
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f)
    
    modify_zip_file(invalid_path, modify_manifest)
    assert validate_oasf(invalid_path) is False

def test_missing_file(valid_oasf_path, tmp_path):
    """Prueba con archivo faltante"""
    invalid_path = str(tmp_path / "demo_missing.zip")
    shutil.copy(valid_oasf_path, invalid_path)
    
    def modify_manifest(temp_dir):
        manifest_path = temp_dir / "MANIFEST.json"
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        
        manifest["audio_tracks"][0]["path"] = "tracks/audio/nonexistent.wav"
        
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f)
    
    modify_zip_file(invalid_path, modify_manifest)
    assert validate_oasf(invalid_path) is False