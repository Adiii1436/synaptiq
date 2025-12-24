import PyInstaller.__main__
import os
import shutil

def build_executable():
    print("🚀 Starting Build Process for Synaptiq...")

    # Define the PyInstaller arguments
    args = [
        'app.py',                           # Your main entry point
        '--name=Synaptiq',                  # Name of the output exe
        '--noconsole',                      # Hide the command line window (GUI mode)
        '--clean',                          # Clean PyInstaller cache
        
        # --- Critical Hidden Imports ---
        # Scikit-learn and Torch often fail without these specific hidden imports
        '--hidden-import=sklearn.utils._typedefs',
        '--hidden-import=sklearn.utils._heap',
        '--hidden-import=sklearn.utils._sorting',
        '--hidden-import=sklearn.utils._vector_sentinel',
        '--hidden-import=sklearn.neighbors._partition_nodes',
        '--hidden-import=sklearn.metrics._pairwise_distances_reduction',
        '--hidden-import=sklearn.metrics._pairwise_fast',
        
        # Ensure these are bundled
        '--hidden-import=sentence_transformers',
        '--hidden-import=ollama',
        '--hidden-import=pypdf',
        '--hidden-import=docx',
        '--hidden-import=pptx',
        '--hidden-import=openpyxl',
        
        # --- Optimization ---
        # Exclude heavy libraries not used in your code to save space
        '--exclude-module=tkinter',
        '--exclude-module=matplotlib',
        '--exclude-module=ipykernel',
        '--exclude-module=notebook',
        
        # --- Output Mode ---
        # 'onedir' creates a folder with the exe inside. 
        # It is FASTER to start up and easier to debug than 'onefile'.
        # If you strictly want a single file, change this to '--onefile'
        '--onedir', 
    ]

    # Run PyInstaller
    PyInstaller.__main__.run(args)

    print("\n✅ Build Complete!")
    print(f"📁 content located in: {os.path.join(os.getcwd(), 'dist', 'Synaptiq')}")

if __name__ == "__main__":
    build_executable()