REM �t�@�C���ҏW
set pypath=%~dp0
echo %pypath%
echo %1
for /f "usebackq" %%t in (`%pypath%melon�ҏW.py "%1"`) do set work=%%t
echo %work%

REM �r�����[�ɊJ������
"C:\Program Files (x86)\Melonbooks\melonbooksviewer\melonbooksviewer.exe" %work%

REM temp�ɕۑ����ꂽ�t�@�C�����R�s�[����
set out=%work:.melon=%
echo %out%
copy %temp%\Melonbooks\temporary.pdf "%out%"

REM Acrobat�������I��
taskkill /f /im AcroRd32.exe
