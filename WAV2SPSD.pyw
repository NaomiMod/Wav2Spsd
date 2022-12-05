# -----------------------
# WAV2SPSD.pyw
#
# By VincentNL 2022/12/04
# -----------------------
#        NOTES:
# -----------------------
#
# 1. Place "Mkstream.exe" and "wavecon.exe" in "tools" folder
#   (You can find them both in Katana SDK r10)
# 2. Place config.txt in the same folder where you run the script
#
# -----------------------
#     SPECIAL THANKS:
# -----------------------
#
# - vgmstream for their excellent documentation
#   on .str / .spsd playback!
#
# - Sappharad for .adx / .str info
#
# - Alexvgz for testing
#
# - Zocker160 for easystruct
# ------------------------

import easystruct as bin
import math
import os
from scipy.io import wavfile
import subprocess
import tkinter as tk
from tkinter import filedialog

debug = False

root = tk.Tk ()
root.withdraw ()
filenames = filedialog.askopenfilenames (initialdir=".", title="Choose a .WAV file to convert (Stereo)",
                                         filetypes=[(".wav", "wav")])
selected_files = len (filenames)         # Number of files to convert

## Config File:
config_file = open ('config.txt', 'r')
config = config_file.read()
SPSD_output=int(config[config.find('spsd_output=')+12:config.find('spsd_output=')+14])  # read configuration value

if debug: print (filenames,SPSD_output)


def wav_check():
    global freq, f, supported_freq, stereo
    # ---------------------
    # Check Src Wav File
    # ---------------------

    f = open (filename, 'rb')  # Open src .WAV file
    iswave = f.read (0x4)  # Check if RIFF header
    f.seek (0x16)
    stereo = int.from_bytes (f.read (0x2), "little")  # Check if Stereo
    freq = int.from_bytes (f.read (0x4), "little")  # Check wave frequency
    supported_freq = [8000, 11025, 16000, 22050, 30000, 32000, 44100]  # Supported freqs

    if debug: print (iswave, freq, stereo)
    f.close ()

    # -------
    # Errors
    # -------
    if iswave != b'RIFF':
        print (f'{filename} is not a .wav file!')
        exit ()

    if stereo != 2:
        print (f'{filename} is not a stereo .wav file!')
        exit ()

    if freq not in supported_freq:
        print (f'{filename}, {freq}Hz is an unsupported frequency!')
        exit ()


def spsd_header():
    # ----------------
    # Write SPSD file
    # ----------------

    ## SPSD Header
    header_1 = b'\x53\x50\x53\x44\x01\x01\x00\x04\x03'
    header_2 = b'\xF7\x1F\xF7\x1F\xF7\x1F\xF7\x1F\xF7\x1F\x00\x00\x00\x00\x04\x01\x00\x00'
    header_3 = b'\x1F\00\x1F\x00\x00\xBC'
    header_4 = b'\xC0\x4A\x09\x00\x0F\x7F\x1F\x00\x0F\x7F\x0F\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    speed_list = [27072, 28672, 29184, 30720, 31089, 31223, 0]  # Assign a fixed speed value fm 8000-44100Hz
    speed = speed_list[supported_freq.index (freq)]

    if stereo > 1:
        stereo_val = 0x01
    else:
        stereo_val = 0x00

    if SPSD_type == 1:
        SPSD_format = 0xd  # Use fixed steps of 0x2000
    elif SPSD_type == 2:
        SPSD_format = 0xff  # Use fixed steps of 0x800

    ## Rebuild .SPSD header

    n.write (header_1)
    bin.write_uint8_buff (n, stereo_val)
    bin.write_uint16_buff (n, SPSD_format)
    bin.write_uint32_buff (n, size)
    n.write (header_2)
    bin.write_uint16_buff (n, (speed))
    n.write (header_3)
    bin.write_uint16_buff (n, freq)
    n.write (header_4)

def wav2spsd_v1():     # V1 is one of the mostly used spsd format
    global n, size

    fs, data = wavfile.read (filename)  # read wav file, split into 2 mono tracks
    wavfile.write (filename[:-4] + '_left.wav', fs, data[:, 0])  # channel 1
    wavfile.write (filename[:-4] + '_right.wav', fs, data[:, 1])  # channel 2
    cmd = [fr'{os.getcwd ()}\tools\wavecon.exe', f'{filename[:-4]}_left.wav']
    cmd1 = [fr'{os.getcwd ()}\tools\wavecon.exe', f'{filename[:-4]}_right.wav']
    subprocess.run (cmd, shell=True)
    subprocess.run (cmd1, shell=True)

    ## Startup, load ADPCM tracks, initialize target .SPSD

    l = open (f'{filename[:-4]}_left.adp', 'rb')  # left channel
    r = open (f'{filename[:-4]}_right.adp', 'rb')  # right channel
    n = open (f'{filename[:-4]}_v1.spsd', 'w+b')  # initialize target
    n = open (f'{filename[:-4]}_v1.spsd', 'a+b')  # start append

    ## SPSD conversion params
    size = len (r.read ()) + len (
        l.read ())  # Remove header of 0x800 stream data from left and right .STR files
    data_shift = 0x2000
    l.seek (0x0)  # Start read from left channel
    r.seek (0x0)  # Start read from right channel

    spsd_header ()  # rebuild header

    ## Calculate number of steps for data shifting
    ttl_steps = math.ceil (size / data_shift - 1)

    if debug: print ("\nInterleave blocks:", (ttl_blocks))
    if debug: print ("Ttl.size:", hex (size), "\nSteps:", (ttl_steps))

    cur_step = 1

    ## Write SPSD data:
    while cur_step <= ttl_steps:
        n.write (l.read (data_shift))
        n.write (r.read (data_shift))
        cur_step += 1

    ## Cleanup:

    n.close ()
    f.close ()
    l.close ()
    r.close ()
    os.remove (f'{filename[:-4]}_left.adp')
    os.remove (f'{filename[:-4]}_right.adp')
    os.remove (f'{filename[:-4]}_left.wav')
    os.remove (f'{filename[:-4]}_right.wav')

def wav2spsd_v2():     # V2 is used on newer Naomi / Naomi2 games, i.e. Virtua Tennis 2, Initial D3
    global n, size

    cmd = [fr'{os.getcwd ()}\tools\MkStream.exe', f'{filename}', f'{filename[:-4]}_v2.str', 'adpcm']
    subprocess.run (cmd, shell=True)

    f = open (f'{filename[:-4]}_v2.str', 'rb')  # .STR file
    n = open (f'{filename[:-4]}_v2.SPSD', 'w+b')  # initialize target
    n = open (f'{filename[:-4]}_v2.SPSD', 'a+b')  # start append

    # ---------------------
    # Read STR Header file
    # ---------------------

    f.seek (0x4)
    freq = bin.read_uint32_buff (f)
    encoding = bin.read_uint32_buff (f)
    interleave = bin.read_uint32_buff (f)
    f.seek (0x14)
    samples = bin.read_uint32_buff (f)
    channels = bin.read_uint8_buff (f)

    if channels > 1:
        stereo_flag = "Stereo"
        interleave_flag = f"\nInterleave block size: {interleave}"
    else:
        stereo_flag = "Mono"
        interleave_flag = ""

    if encoding == 4:
        encoding_flag = "ADPCM"
    elif encoding == 16:
        encoding_flag = "PCM16"
    else:
        encoding_flag = "UNK"

    if channels > 1:
        interleave = "interleave"
    else:
        interleave = "no interleave",

    if debug: print (
        "STR file parameters\n-------------", "\nChannels:", (channels), (stereo_flag),
        interleave_flag, "\nSamples:", samples, "\nSample rate:", freq, "Hz", "\nEncoding:",
        (encoding_flag), f"[{hex (encoding)}]"
    )

    ## .STR conversion params
    f.seek (0x0)
    size = int ((len (f.read ()) - (0x800))) 
    f.seek (0x800)  # Start reading data

    spsd_header ()  # rebuild header

    ## Number of interleave blocks if Stereo
    if channels > 1:
        data_shift = 0x800
        ttl_steps = math.ceil ((size / data_shift - 1))
        if debug: print ("\nInterleave blocks:", (ttl_steps))

    else:
        data_shift = 0
        ttl_steps = 1

    if debug: ("Ttl.size:", hex (size))

    cur_step = 1

    ## Write SPSD data:

    if channels > 1:
        while cur_step <= ttl_steps:
            n.write (f.read (data_shift))  # left channel
            f.seek (f.tell () + data_shift)
            cur_step += 1

        cur_step = 1

        f.seek (0x800 + data_shift)
        while cur_step <= ttl_steps:
            n.write (f.read (data_shift))  # right channel
            f.seek (f.tell () + data_shift)
            cur_step += 1

    else:
        n.write (f.read ())

    ## Cleanup:
    n.close ()
    f.close ()
    os.remove (f'{filename[:-4]}_v2.str')

    if debug: print ("Done!")


# ---------
# Main Loop
# ---------

current_file = 0

while current_file < selected_files:  # Process all selected files in the list
    filename = filenames[current_file]
    wav_check ()

    if SPSD_output == 1:
        SPSD_type = 1
        wav2spsd_v1 ()

    elif SPSD_output == 2:
        SPSD_type = 2
        wav2spsd_v2 ()

    elif SPSD_output == 3:
        SPSD_type = 1
        wav2spsd_v1 ()
        SPSD_type = 2
        wav2spsd_v2 ()

    current_file += 1
