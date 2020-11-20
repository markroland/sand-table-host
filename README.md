# Sand Table Host

## Hardware Recommendations

 - [Raspberry Pi 3](https://www.adafruit.com/category/105)
 - [Synthetos gShield v5](https://synthetos.myshopify.com/products/gshield-v5)
 - [Arduino Uno](https://www.sparkfun.com/products/11021)
 - Stepper Motors
 - Power Supply
  - Stepper Motors
  - Arduino
  - Raspberry Pi

## Software Recommendations

 - Python 3.5+


## Circuit

```
TBD
```


## Usage

### Run as script that will continue if connection is lost
```
echo y | nohup python3 ~/Documents/Sand\ Table/sand-table-player.py playlist-1 --delay=60
```

### Set coordinates in Universal Gcode Sender (UGS)

This is helpful if the calibration gets off or the connection has to be reset.

```
G10 P0 L20 X422 Y4
```


## Resources

- [GRBL](https://github.com/gnea/grbl)


## License

[![Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://i.creativecommons.org/l/by-nd/2.0/88x31.png)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

This work is licensed under a [Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)](https://creativecommons.org/licenses/by-nc-sa/4.0/) License.
