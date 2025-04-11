# src/tools/validate_oasf.py
import hashlib
import json
import zipfile
from pathlib import Path
import shutil

def calculate_sha3_512(file_path: Path) -> str:
    """Calcula hash SHA3-512 de un archivo"""
    sha = hashlib.sha3_512()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return f"sha3-512:{sha.hexdigest()}"

def validate_oasf(oasf_path: str) -> bool:
    """Valida la estructura y hashes de un archivo .oasf"""
    temp_dir = Path("temp_validation")
    try:
        temp_dir.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(oasf_path, "r") as zip_ref:
            # Buscar MANIFEST.json
            manifest_files = [f for f in zip_ref.namelist() if Path(f).name == "MANIFEST.json"]
            if not manifest_files:
                print("❌ MANIFEST.json no encontrado")
                return False
            
            manifest_path = manifest_files[0]
            zip_ref.extract(manifest_path, temp_dir)
            
            # Leer MANIFEST.json
            manifest_full_path = temp_dir / manifest_path
            with open(manifest_full_path, "r") as f:
                manifest = json.load(f)
            
            # Validar hashes de audio
            for track in manifest.get("audio_tracks", []):
                file_in_zip = str(Path(manifest_path).parent / track["path"])
                if file_in_zip not in zip_ref.namelist():
                    print(f"❌ Archivo de audio no encontrado: {file_in_zip}")
                    return False
                
                zip_ref.extract(file_in_zip, temp_dir)
                current_hash = calculate_sha3_512(temp_dir / file_in_zip)
                
                if current_hash != track["hash"]:
                    print(f"❌ Hash inválido en {track['path']}")
                    print(f"  Esperado: {track['hash']}")
                    print(f"  Obtenido: {current_hash}")
                    return False
            
            print("✅ .oasf válido")
            return True
            
    except Exception as e:
        print(f"❌ Error crítico: {str(e)}")
        return False
        
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)

# Esto evita que se ejecute código al importar
if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python validate_oasf.py <archivo.oasf>")
        sys.exit(1)
    validate_oasf(sys.argv[1])