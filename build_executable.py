import os
import sys
import shutil
import subprocess

def build_executable():
    """Build a standalone executable for the Lego Mosaic Generator"""
    print("Building Lego Mosaic Generator executable...")
    
    # Make sure PyInstaller is installed
    try:
        import PyInstaller
        print("PyInstaller already installed")
    except ImportError:
        print("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Create a directory for the build files
    if not os.path.exists("build"):
        os.makedirs("build")
    
    # Create a directory for the dist files
    if not os.path.exists("dist"):
        os.makedirs("dist")
    
    # Create the spec file contents with proper resource handling
    spec_content = """
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['lego_mosaic_generator.py'],
    pathex=[],
    binaries=[],
    datas=[('Lego Colors.xlsx', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Lego Mosaic Generator',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='NONE',
)
    """
    
    # Write the spec file
    with open("lego_mosaic_generator.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller
    print("Running PyInstaller...")
    subprocess.check_call([
        sys.executable, 
        "-m", 
        "PyInstaller", 
        "lego_mosaic_generator.spec",
        "--clean"
    ])
    
    # Create output directory for the final release
    output_dir = "Lego_Mosaic_Generator_Release"
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)
    
    # Copy the executable and other required files to the output directory
    shutil.copytree("dist/Lego Mosaic Generator", output_dir + "/Lego Mosaic Generator")
    shutil.copy("README.md", output_dir)
    
    # Create a directory for sample images
    os.makedirs(os.path.join(output_dir, "Images"), exist_ok=True)
    
    # Copy sample image if available
    if os.path.exists("Images/StarryNight.jpg"):
        shutil.copy("Images/StarryNight.jpg", os.path.join(output_dir, "Images"))
    
    print(f"\nBuild completed successfully!")
    print(f"The executable is located in: {os.path.join(os.getcwd(), output_dir, 'Lego Mosaic Generator')}")
    print("To run the application, double-click the 'Lego Mosaic Generator.exe' file in that folder.")

if __name__ == "__main__":
    build_executable() 