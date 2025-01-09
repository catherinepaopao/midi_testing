from midiutil import MIDIFile
import boto3

# degrees  = [60, 62, 64, 65, 67, 69, 71, 72]  # MIDI note number
# degrees2  = [64, 65, 67, 69, 71, 72, 60, 62]  # MIDI note number
# track    = 0
# channel  = 0
# time     = 0    # In beats
# duration = 1    # In beats
# tempo    = 60   # In BPM
# volume   = 100  # 0-127, as per the MIDI standard

# MyMIDI = MIDIFile(2)  # Number of tracks
# MyMIDI.addTempo(track, time, tempo) # add each track, track number first
# MyMIDI.addTempo(track + 1, time, tempo)

# for i, pitch in enumerate(degrees): # add pitches to tracks
#     MyMIDI.addNote(track, channel, pitch, time + i, duration, volume)

# for i, pitch in enumerate(degrees2):
#     MyMIDI.addNote(track + 1, channel, pitch, time + i, duration, volume)

# with open("major-scale.mid", "wb") as output_file:
#     MyMIDI.writeFile(output_file)

def generate_midi(track_count, tempo, time, track_specs, output_name):
    myMIDI = MIDIFile(track_count)

    for i in range(track_count):
        myMIDI.addTempo(i, time, tempo)
        specs = track_specs[i]
        note_count = specs["note_count"]
        channels = specs["channels"]
        pitches = specs["degrees"]
        durations = specs["durations"]
        volumes = specs["volumes"]
        
        total_duration = 0
        for j in range(note_count):
            myMIDI.addNote(i, channels[j], pitches[j], time + total_duration, durations[j], volumes[j])
            total_duration += durations[j]
    
    with open(output_name + ".mid", "wb") as output_file:
        myMIDI.writeFile(output_file)
        

def generate_track_specs(track_count, note_count_list, degrees_list, durations_list, volumes_list, channels_list):
    track_specs = []
    for i in range(track_count):
        specs = {"note_count": note_count_list[i], 
            "degrees": degrees_list[i],
            "durations": durations_list[i],
            "volumes": volumes_list[i],
            "channels": channels_list[i]}
        
        track_specs.append(specs)
    
    return track_specs

def generate_response(prompt, system_text=None, model='anthropic.claude-3-5-sonnet-20240620-v1:0'):
    client = boto3.client('bedrock-runtime')
    result = client.converse(
        modelId=model,
        messages=[
            {
                'role': 'user',
                'content': [{
                    'text': prompt
                }]
            }
        ],
        system=[
            {
                'text': system_text
            }
        ],
    ) 

    response = result["output"]["message"]["content"][0]["text"] # actual message
    return response

def parse_response(response):
    NUMBERS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '.']
    responses = response.split('\n')

    melody = []
    next_num = ''
    for char in responses[0]:
        if char in NUMBERS:
            next_num += char
        
        elif char == ',' or char == ']':
            melody.append(int(next_num))
            next_num = ''

    rhythm = []
    for char in responses[1]:
        if char in NUMBERS:
            next_num += char
        
        elif char == ',' or char == ']':
            rhythm.append(float(next_num))
            next_num = ''
        
    return (melody, rhythm)

if __name__ == "__main__":
    # tracks = 2
    # note_counts = [14, 14]
    # degrees = [[60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60], [60, 60, 67, 67, 69, 69, 67, 69, 69, 67, 67, 65, 65, 64]]
    # durations = [[1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2], [1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2]]
    # volumes = [[100]*14, [100]*14]
    # channels = [[0]*14, [0]*14]
    # tempo = 60 
    # time = 0
    SYSTEM_TEXT = "Write an interesting melody using midi note numbers based on a given description. Output the notes as a list called \"melody\", and output another list called \"rhythm\" of the same length that specifies durations of each corresponding note in beats. Do not add any additional text."
    PROMPT = "Generate a sad melody"

    tracks = 1
    note_counts = [0]
    tempo = 60
    time = 0

    response = generate_response(PROMPT, SYSTEM_TEXT)
    print(response)
    lists = parse_response(response)
    melody = lists[0]
    rhythm = lists[1]

    print(lists)

    note_counts[0] = len(melody)
    degrees = [melody]
    durations = [rhythm]
    volumes = [[100]*note_counts[0]]
    channels = [[0]*note_counts[0]]

    track_specs = generate_track_specs(tracks, note_counts, degrees, durations, volumes, channels)

    generate_midi(tracks, tempo, time, track_specs, "generation/testing")