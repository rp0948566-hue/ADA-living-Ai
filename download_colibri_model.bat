@echo off
REM Downloads the GLM-5.2 colibri model (~429 GB) to C:\colibri_models\glm52_i4
REM Safe to close and re-run this file any time - it resumes where it left off.
D:\Jarvis.v3.0-main-main\.venv\Scripts\hf.exe download mastouri/GLM-5.2-colibri-int4-g64-with-int8-mtp --local-dir C:\colibri_models\glm52_i4
pause
