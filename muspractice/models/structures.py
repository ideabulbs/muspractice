import random

class Notes:
	NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'Ab', 'A', 'Bb', 'B']

class Chords:
	NOTES = Notes.NOTES
	EXTENSIONS = ['maj', 'min', 'dim', 'aug', '7', 'm7', 'maj7', 'm9', 'maj9', '9', 'sus4', 'm7b5']
	METHODS = ['Rhythm', 'Walking bass', 'Plucking']

class Arpeggios:
	NOTES = Notes.NOTES
	EXTENSIONS = Chords.EXTENSIONS
	METHODS = ['3rds', '5ths', '3rds full range', '5ths full range']

class Progressions:
	NOTES = Notes.NOTES
	PROGRESSIONS = [ 'I - IV - V - I',
					 'I - V - IV - I',
					 'IIm7 - V7 - Imaj7',
					 'IIm7 - V7 - Imaj7 - VIm7',
					 'IIIm7 - bIIIm7 - IIm7 - Imaj7']
	METHODS = Chords.METHODS

class Scales:
    NOTES = Notes.NOTES
    MODES = ['Ionian',
			 'Dorian',
			 'Phrygian',
			 'Lydian',
			 'Mixolydian',
			 'Aeolian',
			 'Locrian'
			 'Major pentatonic',
			 'Minor pentatonic']

    METHODS = ['Sequential',
			   'Fragmented',
			   'Sequential full range',
			   'Fragmented full range'
    ]

    INTERVALS = ['2nds',
				 '3rds',
				 '4ths',
				 '5ths',
				 '6ths',
				 '7ths']

class Dynamics:
	DYNAMICS = ['Forte',
				'Piano',
				'Innuendo',
				'Diminuendo'
	]

class NoteConnection:
	NOTE_CONNECTION = [
		'Legato',
		'Normal',
		'Staccato'
	]
