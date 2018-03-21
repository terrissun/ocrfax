AutoFAX
by MERS (Siying Sun, Rongrong miao, Matthew and Elaine Chao)

This is a rogram which automatically scans incoming faxes for relevant information, then uploads it to the patient’s chart, filling in the appropriate information based on a scan of the text in the document. The program could also alert doctors of essential lab results that need to be looked at right away. By automating this process, this could prevent a lot of unnecessary organizational work. 





Running the main program:
$ python3 main.py

To configure the program for your operating system, modify the config.ini file.
DefaultTemplateLocation is where the program will save your templates.
DefaultPDFLocation is where the program will open to look for PDFs.
Do NOT commit this file. There should be a .gitignore to prevent this.

Platform: *nix
python version: 3.6.1
Dependencies: 
- kivy garden backend matplotlib 
	- Note: for this dependency, you will first need to install kivy-garden via "pip3 install kivy-garden". You can try "garden install matplotlib", but it may not work. If this is the case, on Ubuntu, change directory to ~/.local/bin, and run "python3 garden install matplotlib". It should work from there.
- tesseract 3.04.01   -sudo apt-get install tesseract-ocr
- pillow    -pip3 install pillow
- tesserocr   - sudo apt-get install tesseract-ocr libtesseract-dev libleptonica-dev , pip3 install tesserocr
- kivy 1.10.0 - sudo apt-get install python3-kivy
- numpy 1.14.0
- matplotlib 2.0.2
- watchdog 0.8.3
- pyyaml 3.12
- argh 0.26.2
- argparse 1.4.0
- pathtools
- sortedcontainers 1.5.9 - pip3 install sortedcontainers
- PyPDF2

For linting:
 Pylint 1.8.3 - pip3 install pylint
 Run by using python3 -m pylint (name of file to lint)

Note: If you need to install or add a package for your code to run, please list it here, under dependencies, if you're not adding it to the Github!

IMPORTANT KIVY CONFIG NOTES:
- when using a trackpad, Kivy can experience weird input issues on Ubuntu, due to trying to register the trackpad as both a touchscreen and a mouse. To disable this, go to the kivy config.ini file (under Ubuntu, located at ~/.kivy/config.ini) and under the [input] section, delete the entry related to probesys. This disables the touchscreen functionality.

- by default, Kivy allows for simulated multitouch by right clicking with the mouse. To disable this, in the kivy config file, under the [input] section, change the line "mouse = mouse" to "mouse = mouse,disable_multitouch"

