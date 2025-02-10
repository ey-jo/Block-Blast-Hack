# Block-Blast-Hack
Python Script to play Block Blast using android debug bridge


### Requirements
- install [python](https://www.python.org/downloads/)
- ```pip install pure-python-adb```
- download android [SDK Platform-Tools](https://developer.android.com/tools/releases/platform-tools)


### Installation on Linux
```bash
pacman -S python-pip
pip -u install pure-python-adb
wget https://dl.google.com/android/repository/platform-tools-latest-linux.zip
unzip platform-tools-latest-linux.zip
cd platform-tools/
adb devices
```
Then start the server using this command in the directory
```bash
adb start-server
```

Enable USB Debugging in the developer settings on the connected Android Device and authorize the computer in the settings.




## Known Issues:

- Sometimes breaks itself because it picks the wrong piece, probably the move index is not translated into the piece of the position correctly. Pieces stay until the next round.

- When only a few pieces are on the grid, calculation of all pieces takes a long time, choose the move differently, if ~70% of grid is empty. 

- Not sure if the 3 pieces the game chooses every round fit in any case.

- pieces are misplaced sometimes