# -*- mode: python -*-

block_cipher = None


a = Analysis(['one.py'],
             pathex=['E:\\python_projects\\xxone'],
             binaries=[],
             datas=[('msg1.wav', '.'), ('title.ico', '.'), ('query.png', '.'), ('msg2.wav', '.'), ('close.gif', '.')],
             hiddenimports=['docx', 'pynput'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='one',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='app.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               name='one')
