@echo off
title Dark Pattern Intelligence System (DPIS)
echo ============================================================
echo  Dark Pattern Intelligence System (DPIS)
echo  Starting local analytics dashboard...
echo ============================================================
echo.
set PYTHON_EXE=C:\Users\yamini reddy\anaconda3\python.exe
"%PYTHON_EXE%" -m streamlit run app/app.py
pause
