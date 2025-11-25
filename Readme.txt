*** How to Install Peppy Meter
*** This is working on Ultra Wide Screen 14 Inches HDMI display
*** The resolution is 1280x400

1.Install peppyalsa

sudo apt install git
git clone https://github.com/project-owner/peppyalsa.git
cd peppyalsa

*** New version of diept will cause peppyalsa compile error 
*** Copy peppyalsa sourcecode  meter.c,spectrum.c peppyalsa.c to replace 
the existing one under /home/dietpi/peppyalsa/src


sudo apt-get install build-essential autoconf automake libtool libasound2-dev libfftw3-dev
aclocal && libtoolize
autoconf && automake --add-missing
./configure && make

sudo make install

sudo mkfifo /var/tmp/peppyfifo
sudo chmod 777 /var/tmp/peppyfifo

2. Configure alsa.conf
Modify from asound.conf to match your soundcard. 
Use aplay -l  to seee card and device id


3. Test peppyalsa after config around.conf
cd /home/dietpi/peppyalsa/src
gcc peppyalsa-client.c -o peppyalsa-client
/home/dietpi/peppyalsa/src/peppyalsa-client /var/tmp/peppyfifo

*** You should see meter moving . if it is not moving , recheck asound.conf 

5. Install PeppyMeter
cd /home/dietpi
git clone https://github.com/project-owner/PeppyMeter.git
sudo apt-get install python3-pygame
sudo apt install python3-pip -y
pip3 install requests —break-system-packages

cd /home/pi/PeppyMeter

(In case of any error downloading Pygame, please use the following command:
sudo apt update —allow-releaseinfo-change

going to replace the content of only the lines below and leaving everything else unchanged:
or copy config.txt to replace your system

meter.folder =1280x400
exit.on.touch = True
framebuffer.device = /dev/fb0
mouse.device = /dev/input/event0
double.buffer = False
pipe.name = /var/tmp/peppyfifo

Run test 
cd /home/pi/PeppyMeter
DISPLAY=:0 python3 peppymeter.py

6. Install as the Service 
copy fda_startpeppy.py and fda_start_peppy.service to /home/dietpi/PeppyMeter
sudo cp fda_startpeppy.service /etc/systemd/system/ 
sudo chmod +111 /etc/systemd/system/fda_startpeppy.service
sudo systemctl daemon-reload
sudo systemctl enable fda_startpeppy.service
sudo systemctl start fda_startpeppy.service
