import json
import zipfile
import shutil  # <-- Añade esto al inicio
from pathlib import Path

def find_manifest(zip_ref):
    for file in zip_ref.namelist():
        if Path(file).name == "MANIFEST.json":
            return file
    return None

def validate_oasf(oasf_path: str) -> bool:
    temp_dir = Path("temp_validation")  # Mover aquí para acceso en finally
    try:
        with zipfile.ZipFile(oasf_path, 'r') as zip_ref:
            manifest_path = find_manifest(zip_ref)
            if not manifest_path:
                print("❌ MANIFEST.json no encontrado")
                return False

            temp_dir.mkdir(exist_ok=True)
            zip_ref.extract(manifest_path, temp_dir)
            manifest_full_path = temp_dir / manifest_path
            
            with open(manifest_full_path, 'r') as f:
                manifest = json.load(f)

            manifest_parent = Path(manifest_path).parent
            for track in manifest.get('tracks', []):
                file_in_zip = str(manifest_parent / track['path'])
                if file_in_zip not in zip_ref.namelist():
                    print(f"❌ Archivo no encontrado: {file_in_zip}")
                    return False

            print("✅ .oasf válido!")
            return True

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

    finally:
        # Borra todo el directorio temporal (archivos + carpetas)
        if temp_dir.exists():
            shutil.rmtree(temp_dir)  # <-- ¡Esto lo soluciona!

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Uso: python validate_oasf.py <ruta/a/proyecto.oasf>")
        sys.exit(1)
    validate_oasf(sys.argv[1])