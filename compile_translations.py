#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to compile Django translation files (.po to .mo) using polib
"""
import os
import sys

try:
    import polib
except ImportError:
    print("Installing polib...")
    os.system("pip install polib")
    import polib

def compile_po_to_mo(po_file, mo_file):
    """Compile a .po file to .mo file"""
    try:
        po = polib.pofile(po_file)
        po.save_as_mofile(mo_file)
        print(f"✓ Compiled: {po_file} -> {mo_file}")
        return True
    except Exception as e:
        print(f"✗ Error compiling {po_file}: {e}")
        return False

def main():
    locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
    
    if not os.path.exists(locale_dir):
        print("Locale directory not found!")
        return
    
    compiled = 0
    for lang in ['en', 'vi']:
        po_file = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.po')
        mo_file = os.path.join(locale_dir, lang, 'LC_MESSAGES', 'django.mo')
        
        if os.path.exists(po_file):
            if compile_po_to_mo(po_file, mo_file):
                compiled += 1
        else:
            print(f"⚠ File not found: {po_file}")
    
    if compiled > 0:
        print(f"\n✓ Successfully compiled {compiled} translation file(s)!")
    else:
        print("\n⚠ No translation files were compiled.")

if __name__ == '__main__':
    main()
