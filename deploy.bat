@echo off
chcp 65001 > nul

:: Hozirgi sana va vaqtni olish (YYYY-MM-DD HH:MM formatida)
for /f "tokens=1-3 delims=/. " %%a in ("%date%") do set mydate=%%c-%%b-%%a
set mytime=%time:~0,5%
set datetime=%date% %mytime%

echo 🚀 Git avtomatlashtirish boshlandi...
echo 📅 Commit vaqti: %datetime%
echo ----------------------------------------

:: Git buyruqlari
git add .
git commit -m "update: %datetime%"
git push origin master

echo ----------------------------------------
echo ✅ Barcha o'garishlar GitHub'ga yuklandi!
pause