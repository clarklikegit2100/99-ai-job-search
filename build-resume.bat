@echo off
setlocal

set "REPO_DIR=%~dp0"
set "SOURCE_FILE=%REPO_DIR%cv-output\main_example-jian.tex"
set "OUTPUT_DIR=%REPO_DIR%cv-output"

where lualatex >nul 2>nul
if errorlevel 1 (
  echo ERROR: lualatex was not found in PATH.
  echo Install MiKTeX or TeX Live, then reopen the terminal.
  exit /b 1
)

if not exist "%SOURCE_FILE%" (
  echo ERROR: Resume source not found: "%SOURCE_FILE%"
  exit /b 1
)

echo Building main_example-jian.pdf...
lualatex --interaction=nonstopmode --halt-on-error --output-directory="%OUTPUT_DIR%" "%SOURCE_FILE%"
if errorlevel 1 exit /b 1

lualatex --interaction=nonstopmode --halt-on-error --output-directory="%OUTPUT_DIR%" "%SOURCE_FILE%"
if errorlevel 1 exit /b 1

echo.
echo PDF created: "%OUTPUT_DIR%\main_example-jian.pdf"
endlocal
