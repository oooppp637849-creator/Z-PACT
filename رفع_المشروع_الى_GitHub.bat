@echo off
chcp 65001 > nul
title Z-PACT - رفع تلقائي إلى GitHub
color 0b

echo ==============================================================
echo              Z-PACT - الرفع التلقائي إلى GitHub
echo ==============================================================
echo.
echo [1/2] جار تنظيف ملفات الاختبار والاسكربتات الزائدة...
echo [2/2] جار رفع المشروع إلى: https://github.com/oooppp637849-creator/Z-PACT
echo.
echo ==============================================================
echo.

cd /d "%~dp0"
if exist "push_to_github.py" (
    python push_to_github.py
) else if exist "Z-PACT-main\push_to_github.py" (
    cd "Z-PACT-main"
    python push_to_github.py
) else (
    echo [خطأ] لم يتم العثور على سكريبت push_to_github.py!
)

echo.
echo ==============================================================
echo انتهت العملية! اضغط على أي مفتاح للإغلاق...
echo ==============================================================
pause > nul
