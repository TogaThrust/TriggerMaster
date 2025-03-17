import PyInstaller.__main__
from pathlib import Path

HERE = Path(__file__).parent.absolute()
path_to_main = str(HERE / "main.py")

def install():
    PyInstaller.__main__.run([
        path_to_main,
        '--name=TriggerMaster',
        '--distpath=C:/Users/lukew/Downloads',
        '--onefile',
        '--add-data=root/lib/assets/icon.ico;trigger_master_resources/lib/assets/.',
        '--add-data=root/lib/assets/loading.gif;trigger_master_resources/lib/assets/.',
        '--add-data=root/lib/assets/logo.png;trigger_master_resources/lib/assets/.',
        '--add-data=root/lib/assets/help/1.jpg;trigger_master_resources/lib/assets/help/.',
        '--add-data=root/lib/assets/help/2.jpg;trigger_master_resources/lib/assets/help/.',
        '--add-data=root/lib/assets/help/3.jpg;trigger_master_resources/lib/assets/help/.',
        '--add-data=root/lib/assets/help/4.jpg;trigger_master_resources/lib/assets/help/.',
        '--add-data=root/lib/assets/help/5.jpg;trigger_master_resources/lib/assets/help/.',
        '--hidden-import=babel.numbers',
        '--hidden-import=multiprocessing',
        '--hidden-import=multiprocessing',
        '--hidden-import=multiprocessing',
        '--hidden-import=asyncio'
        '--windowed',
        '--noconsole',
        '--icon=root/lib/assets/icon.ico',

        # other pyinstaller options...
    ])