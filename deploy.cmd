rem Build the executable file and place it in the python Scripts folder

pyinstaller --onefile -c "convert_images_to_pdf.py"

copy dist\convert_images_to_pdf.exe %USERPROFILE%\AppData\Local\Programs\Python\Python311\Scripts