# WikiColorize bot

## What
This is the source code for a Python bot that pull random images from Wikipedia, colorize them with ([@algorithmiaio](https://github.com/algorithmiaio "@algorithmiaio")) colorize machine learning algorithm, and post to Twitter ([@WikiColorize](https://twitter.com/WikiColorize "@WikiColorize"))

## Why
For fun. Deep learning is good at those kinds of tasks, Algorithmia has this Colorization Demo that can run without cost, only adding their watermark, Twitter is the right place for those kinds of bots, so the stars aligned.

## How
1. Gets [WikiMedia random file URL ](http://commons.wikimedia.org/wiki/Special:Random/File "WikiMedia random file URL ") and return the main file and metadata via XPath using `lxml`
2. Checks if the WikiMedia file is an image (there is audio, PDF and other file formats that do not matter for this application there) - if not, go back to step 1
3. Checks if it is black and white using `Pillow` to check if the image is monochrome - if not, go back to step 1
4. (Optional Step) Tries to identify if the monochrome image looks like a scanned document using `pytesseract` OCR, if it does, go back to step 1. This step is here because if `Tesseract` doesn't recognize the image as a document, it is more likely that it is a photo
5. Saves the photo and inputs it to [Algorithmia Colorization API](https://demos.algorithmia.com/colorize-photos/ "Algorithmia Colorization Demo API"), that uses Deep Learning to try to guess the right colors for a B&W image, and returns the colorized photo
6. Tweets the colorized photo (with metadata and the URL)

### Limitations
Trying to guess if the image is a photo/picture or a document is not optimal can be improved.

The colorization API is far from perfect for most images. However it is great to see state of the art in the field of automatic colorization with real data.
