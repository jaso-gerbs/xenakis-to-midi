#
# Written by Jason Gerber in 2024
#

from midiutil import MIDIFile
from decimal import *

# Your input data
file = open('input.txt', 'r')
data = file.read()

# Function to check if a string is numeric
def is_numeric(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# Split the data by lines and then by spaces to get individual values
rows = [line.split() for line in data.strip().split('\n')]


# Create a matrix to hold numeric values
matrix = []

# Populate the matrix with numeric values
for row in rows:
    if row and all(is_numeric(value) for value in row):
        numeric_row = [float(value) for value in row]
        matrix.append(numeric_row)
        
        
matrix = [row for row in matrix if row]

velocityColumn = [row[9] for row in matrix]  # Index 8 represents the 9th column

# Finding the maximum value in the velocity column
maxVel = max(velocityColumn)
minVel = min(velocityColumn)

instrument_data = []
with open("instruments.txt", "r") as file:
    for line in file:
        line_data = line.strip().split()
        instrument_data.append(line_data)
        
num_tracks = len(instrument_data)
        

# Function to find an instrument from the class number and instrument number
def find_instrument(class_num, instrument_num, instrument_data):
    for row in instrument_data:
        if int(row[0]) == class_num and int(row[1]) == instrument_num:
            return int(row[3])
            
def assign_channel(class_num, instrument_num, instrument_data):
    for row in instrument_data:
        if int(row[0]) == class_num and int(row[1]) == instrument_num:
            return int(row[5])

# Creates a function to scale numbers
def scale(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
decPitch = False
section_counter = 0  # Initialize section counter
seconds = 0
pitch  = 0 # MIDI note number
track    = 0
channel  = 0
time     = 0   # In beats
duration = 1   # In beats
tempo    = 60  # In BPM
volume   = 100 # 0-127, as per the MIDI standard
resolution = 50
seconds_adder = 0
noteCounter = 0 # Note counter is going to be mod 15, this is how the slight adjustments in pitch work.

MyMIDI = MIDIFile(int(num_tracks), True, False) # One track, defaults to format 1 (tempo track # automatically created)
MyMIDI.addTempo(track,time, tempo)

# Creates tracks and assigns instruments for each instrument in the instruments.txt file       
for row in instrument_data:
    track_name = row[2]
    track_number = int(row[3])
    track_program = int(row[4]) - 1
    track_channel = int(row[5]) - 1
    MyMIDI.addProgramChange(track_number, track_channel, 0, track_program)
    MyMIDI.addTrackName(track_number, 0, track_name)

# Where the magic happens; iterate over each row and assign MIDI values
for row in matrix:
    # Is this row the begining of a section?
    if row[0] == 1:  # Check if the first column value is 1
        section_counter += 1
        seconds_adder = seconds
        print(f"Section {section_counter}:")  # Print section header
    seconds = round((seconds_adder + row[1]), 2)
    
    # Pitch stuff
    if assign_channel(row[2], row[3], instrument_data) == 9: #For ch 10, drum kit
        if row[3] == 10: # Maracas
            pitch = 70
            pitch_decimal = 0
            scaledPitch = 0
        if row[3] == 11: # Susp. Cymbal
            pitch = 49
            pitch_decimal = 0
            scaledPitch = 0
        if row[3] == 12: # Gong
            pitch = 52
            pitch_decimal = 0
            scaledPitch = 0
    if assign_channel(row[2], row[3], instrument_data) == 0: # For channel 1: Wood Block
        if row[3] == 1: # Major pentatonic(?) Sure I guess. This \/ is bad...
            pitch = 60
            pitch_decimal = 0
            scaledPitch = 0
        if row[3] == 2:
            pitch = 62
            pitch_decimal = 0
            scaledPitch = 0
        if row[3] == 3:
            pitch = 64
            pitch_decimal = 0
            scaledPitch = 0
        if row[3] == 4:
            pitch = 67
            pitch_decimal = 0
            scaledPitch = 0
        if row[3] == 5:
            pitch = 69
            pitch_decimal = 0
            scaledPitch = 0
    if assign_channel(row[2], row[3], instrument_data) == 1: # For channel 2: Toms
        if row[3] == 6: # Major pentatonic(?)
            pitch = 60
            pitch_decimal = 0
            scaledPitch = 0
        if row[3] == 7:
            pitch = 62
            pitch_decimal = 0
            scaledPitch = 0
        if row[3] == 8:
            pitch = 64
            pitch_decimal = 0
            scaledPitch = 0
        if row[3] == 9:
            pitch = 67
            pitch_decimal = 0
            scaledPitch = 0
    if row[4] == 0:
        pitch = 60
        pitch_decimal = 0
        scaledPitch = 0
    else:
        pitch = int(row[4]) + 22
        pitch_decimal = round((((row[4]) + 22) - pitch), 1)
        scaledPitch = int(scale(pitch_decimal, 0, 1, 0, 8192))
    
    # Assign instruments
    track = find_instrument(row[2], row[3], instrument_data)
    channel = (assign_channel(row[2], row[3], instrument_data) - 1)
    
    # MIDI duration cannot be zero; .25 is okay.
    if row[8] == 0:
        duration = .25
    else:
         duration = float(row[8])
    
    # Scaled velocity for DYNAM row
    velocity = int(scale(row[9], minVel, maxVel, 20, 127))
    
    # Where the magic happens, for real
    MyMIDI.addNote(track, channel, pitch, seconds, duration, velocity)
    if decPitch == True:    
        channel = noteCounter % 16      
        MyMIDI.addPitchWheelEvent(track, channel, seconds, scaledPitch)
        MyMIDI.addPitchWheelEvent(track, channel, seconds + duration, 0)

        if channel == 8:
            noteCounter =+ 1
        
        noteCounter =+ 1
    
    
    
    print(f"Seconds: {seconds} Pitch (MIDI): {pitch} Pitch Decimal: {pitch_decimal} Duration (s): {duration} Track: {track} Velocity: {velocity} Channel: {channel + 1}")  
    
with open("output.mid", "wb") as output_file:
    MyMIDI.writeFile(output_file)
