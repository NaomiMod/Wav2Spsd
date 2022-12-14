# WAV2SPSD v1.0
By VincentNL 2022/12/04

This program will convert your stereo .wav files [8000-11025-16000-22050-30000-32000-44100Hz] into Naomi .SPSD files.

Please note, SPSD use 2 main format variations with different data layout/header.

Most games use v1, but a number of new titles like InitalD3 (Naomi2) use v2.
For this reason just decided to include both formats as output after conversion.
(If you only need one type, just edit config.txt)

# HOW TO INSTALL


1. Extract this archive into any folder of your choice.
2. Third party tools are required to be placed in "tools" folder:

- wavecon.exe
- MkStream.exe

(*COUGH* SDK/EXES/INSTALL KATANA SDK/INPUT/R10.1_000518/Utl/Snd/PC)

# HOW TO USE

1) Run WAV2SPSD.exe
2) Select .wav file(s) to be converted

# OPTIONS

In program folder you will find a "config.txt" file,
you can customize it to output only a specific .SPSD format or both (by default).

* 1 = V1 which is the most common type
* 2 = V2 used on newer games (Initial D3, Virtua Tennis 2)
* 3 = output both formats (default)

# SPECIAL THANKS

- vgmstream plugin for their excellent documentation on .str / .spsd playback!
 
- Sappharad for .adx / .str info

- Zocker160 for easystruct

- Alexvgz for testing


# LEGAL DISCLAIMER

This project is intended exclusively for educational purposes and has no affiliation with SEGA or any other third party developer.
MkStream.exe and wavecon.exe are exlusive property of SEGA and CANNOT BE DISTRUBUTED/packed with WAV2SPSD V1.0.
If you want to buy me a coffee or show some love:

https://ko-fi.com/vincentnl

https://www.patreon.com/VincentNL
