# Convert images to PDF

## Introduction

Many times you have to create a PDF staring from a list of images. The idea is to run an exe file from any folder on the PC that will take in input some images filename and it will create a PDF file. The order of the images in the PDF will be the same in which the images are passed to the exe. By default the output filename will be **merge.pdf**

## Software and Libraries

This project uses Python 3.9.5 and the following libraries:
* [pyinstaller](https://www.pyinstaller.org/)
* [PIL](https://pillow.readthedocs.io/en/stable/index.html)


More informations in `requirements.txt`. To create it I have used `python -m pip freeze > requirements.txt`. To install all Python packages written in the requirements.txt file run `pip install -r requirements.txt`.

## Data

Have a look at the `data` folder and its [DATA.md](data/DATA.md) file.

## Testing

No test implemented.

## Build

To build the .exe file and place it in **%USERPROFILE%\AppData\Local\Programs\Python\Python39\Scripts**
you have to run `deploy.cmd`

To check the value of the environment variable %USERPROFILE% with Windows PowerShell you have to run `$env:USERPROFILE` while on the command line you can simply run `echo %USERPROFILE%`

## Running the code

From any folder of your PC you can open a command promt and run `convert_images_to_pdf.exe image_1.jpeg image_2.jpeg` and in the same folder a **merge.pdf** file will be created

You can find more information in this [blog post](https://simone-rigoni01.medium.com/easily-convert-images-to-pdf-with-python-540093f38988)


## List of activities

In the [TODO.md](TODO.md) file you can find the list of tasks and on going activities.

## Licensing and Acknowledgements

Have a look at [LICENSE.md](LICENSE.md) and many thanks to [datatofish.com](https://datatofish.com/images-to-pdf-python/#:~:text=%20Steps%20to%20Convert%20Images%20to%20PDF%20using,the%20image%20to%20PDF%20using%20Python%20More%20) for the tips about how to convert images to PDF using python.
