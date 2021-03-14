# -*- mode: python ; coding: utf-8 -*-
import os
spec_root = os.path.abspath(SPECPATH)

block_cipher = None


a = Analysis(['uninstaller\\anyconnect-uninstall.py'],
             pathex=[spec_root],
             binaries=[],
             datas=[('uninstaller\\paths-to-delete.txt', '.'), ('uninstaller\\keys-to-delete.txt', '.')],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
a.datas += [('icon.ico','icon.ico','DATA')]
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='anyconnect-uninstall',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=True,
          icon='icon.ico' )
