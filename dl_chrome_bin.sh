#!/bin/bash 

mkdir chrome_bin

wget https://chromedriver.storage.googleapis.com/2.29/chromedriver_linux64.zip
unzip chromedriver_linux64.zip 
mv chromedriver chrome_bin2
rm chromedriver_linux64.zip 

mkdir -p temp/mount 
curl https://dl.google.com/release2/q/canary/googlechrome.dmg > temp/1.dmg
yes | hdiutil attach -noverify -nobrowse -mountpoint temp/mount temp/1.dmg
cp -r temp/mount/*.app chrome_bin2/
hdiutil detach temp/mount
rm -r $temp
