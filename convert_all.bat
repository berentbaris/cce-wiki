@echo off
cd /d "%~dp0"
python convert_all.py
python generate_wiki.py
exit
