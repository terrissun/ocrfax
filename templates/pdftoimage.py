'''
pdftoimage.py
'''

import PyPDF2
import os
import shutil

def convert_pdf(path):
    name_startindex = 0
    print("Debug: event.src_path is {}".format(path))
    for i in range(len(path)):
        if path[i] == '/':
            name_startindex = i
    filename = path[name_startindex+1:-4]

    # Convert PDF to PNG images
    pdf_file = open(path, 'rb')
    numPages = PyPDF2.PdfFileReader(pdf_file).getNumPages()
    imgFile = os.getcwd() + '/' + filename

    # PNG is created for every page in the PDF
    # The image is moved to a folder named (pdf filename)_images
    imgFolder = os.getcwd() + '/' + filename + "_images"
    # if the folder doesn't exist, create it
    if not os.path.exists(imgFolder):
        os.system("mkdir '%s'" %(imgFolder))

    # for each PDF page, convert it to an image
    for i in range(numPages):
        convCmd = "convert -density 300 '"
        convCmd += path + "'[" + str(i) + "] -depth 8 -background white "
        convCmd += "-flatten +matte +repage -deskew 40% '" + imgFile + '_' + str(i+1) + ".png'"
        os.system(convCmd)
        img = os.getcwd() + '/' + filename + '_' + str(i+1) + ".png"
        shutil.copy(img, imgFolder)

        # rename the file in its respective folder to 1.png, 2.png, etc.
        os.rename('{}/{}_{}.png'.format(imgFolder, filename, i+1), '{}/{}.png'.format(imgFolder, i+1))
        os.system("rm '%s'" %(img)) # remove the image from the current directory

    return imgFolder