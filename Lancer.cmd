@echo off
setlocal
cd /d "%~dp0"

set "QUIZ_NODE="
for /f "delims=" %%N in ('where.exe node.exe 2^>nul') do if not defined QUIZ_NODE set "QUIZ_NODE=%%N"
if not defined QUIZ_NODE if exist "%ProgramFiles%\nodejs\node.exe" set "QUIZ_NODE=%ProgramFiles%\nodejs\node.exe"
if not defined QUIZ_NODE if exist "%LOCALAPPDATA%\Programs\nodejs\node.exe" set "QUIZ_NODE=%LOCALAPPDATA%\Programs\nodejs\node.exe"
if not defined QUIZ_NODE if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" set "QUIZ_NODE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe"
if not defined QUIZ_NODE if exist "%~dp0.tools\node\node.exe" set "QUIZ_NODE=%~dp0.tools\node\node.exe"

if not defined QUIZ_NODE (
    echo Node.js est introuvable sur cet ordinateur.
    echo Installez Node.js depuis https://nodejs.org puis relancez ce fichier.
    echo.
    pause
    exit /b 1
)

echo Demarrage du quiz...
echo Laissez cette fenetre ouverte pendant la session.
echo Pour arreter le serveur, appuyez sur Ctrl+C ou fermez cette fenetre.
echo.

if "%QUIZ_NO_OPEN%"=="1" (
    "%QUIZ_NODE%" "%~dp0scripts\run.mjs" dev -- %*
) else (
    "%QUIZ_NODE%" "%~dp0scripts\run.mjs" dev -- --open %*
)
set "QUIZ_EXIT=%ERRORLEVEL%"
echo.
if not "%QUIZ_EXIT%"=="0" echo Le lancement a echoue. Le message d'erreur figure ci-dessus.
pause
exit /b %QUIZ_EXIT%
