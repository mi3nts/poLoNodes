

~~~
sudo apt update
sudo apt install python3-pip
sudo addgroup teamlary audio
pip3 install sounddevice
sudo apt-get install libportaudio2
sudo apt-get install build-essential libssl-dev libffi-dev python-dev
# Only After this we see all audio devices
sudo apt install libusb-1.0-0-dev
git clone https://github.com/mvp/uhubctl
cd uhubctl/
make
sudo make install
pip3 install paho-mqtt
pip3 install pyserial
pip3 install getmac
pip3 install pynmea2
pip3 install smbus2
pip3 install --extra-index-url https://google-coral.github.io/py-repo/ tflite_runtime
pip3 install scipy
pip3  install pandas
pip3 install librosa==0.9.1
# Add to ~.bashrc
export LD_PRELOAD=/home/teamlary/.local/lib/python3.8/site-packages/scikit_learn.libs/libgomp-d22c30c5.so.1.0.0
~~~
