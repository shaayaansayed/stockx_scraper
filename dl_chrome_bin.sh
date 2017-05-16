#!/bin/bash 

if [[ "$OSTYPE" == "darwin"* ]]; then
	CHROME_DRIVER_PATH='https://chromedriver.storage.googleapis.com/2.29/chromedriver_mac64.zip'
	
	mkdir -p temp/mount 
	curl https://dl.google.com/chrome/mac/dev/GoogleChrome.dmg > temp/1.dmg
	yes | hdiutil attach -noverify -nobrowse -mountpoint temp/mount temp/1.dmg
	cp -r temp/mount/*.app $BIN_DIR/
	hdiutil detach temp/mount
	rm -rf temp
elif [[ "$OSTYPE" == "linux"* ]]; then 
	CHROME_DRIVER_PATH="https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip"
fi
CHROME_DRIVER_FILENAME="${CHROME_DRIVER_PATH##*/}"

BIN_DIR=chrome_bin
mkdir $BIN_DIR

wget $CHROME_DRIVER_PATH
unzip $CHROME_DRIVER_FILENAME
mv chromedriver $BIN_DIR
rm $CHROME_DRIVER_FILENAME