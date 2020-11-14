# Sand Table Host

## Run Playlist

### Run as script that will continue if connection is lost
```
echo y | nohup python ~/Documents/Sand\ Table/sand-table-player.py playlist-1 --delay=60
```

### Set coordinates in Universal Gcode Sender (UGS)

This is helpful if the calibration gets off or the connection has to be reset.

```
G10 P0 L20 X422 Y4
```
