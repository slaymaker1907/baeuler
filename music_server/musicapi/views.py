from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
import os
from music21 import *
import music21
from django.http import HttpResponse
from itertools import groupby, combinations
from math import ceil
import json
import pdb

def lilypond_response(score):
    # fname = score.write(fmt='lily.svg')
    # with open(fname, 'rb') as f:
    #     return HttpResponse(f.read(), content_type='image/svg')
    # pdb.set_trace()
    # score.show()
    conv = converter.subConverters.ConverterMusicXML()
    fname = conv.write(score, 'musicxml')
    muse_score = environment.get('musicxmlPath')
    # output_path = fname.replace('xml', 'png')
    output_path = fname.replace('xml', 'svg')
    command = f'{muse_score} -s -m -r 100 {fname} -o {output_path}'
    print(command)
    os.system(command)
    with open(output_path.replace('.svg', '-1.svg'), 'rb') as f:
        return HttpResponse(f.read(), content_type='image/svg+xml')

# Create your views here.
#@api_view(['GET'])
def chordify_piece(request, piece):
    piece = load_pretty_score(f'{piece}.xml')
    chordified, bass_line = pretty_chordify(piece)
    piece.insert(0, chordified)
    piece.insert(0, bass_line)
    return lilypond_response(piece)

def original_piece(request, piece):
    piece = load_pretty_score(f'{piece}.xml')
    # piece.show()
    return lilypond_response(piece)

def run_analysis_on_piece(request, overlap, piece):
    # First find how to group measures.
    overlap = float(overlap) / 100.0
    piece = load_pretty_score(f'{piece}.xml')
    chordified, bass_line = pretty_chordify(piece)
    # piece.makeNotation(inPlace=True)

    measure_grouping = analyze_piece(chordified, overlap=overlap)
    # print_groups(measure_grouping)
    grouping_it = iter(measure_grouping)

    # Now go through and add slurs in Ch. Bass where grouped.
    measures = list(bass_line.getElementsByClass('Measure'))

    # print([m.measureNumber for m in bass_line.recurse().getElementsByClass('Note')])
    # print([list(m.notes) for m in measures])
    notes_to_slur = list(measures[0].notes)
    for measure in measures[1:]:
        notes = list(measure.notes)
        if next(grouping_it):
            notes_to_slur += notes
        else:
            if len(notes_to_slur) > 1:
                slur = spanner.Slur(notes_to_slur)
                bass_line.insert(0, slur)
            # measure.leftBarLine = bar.Barline('final')
            notes_to_slur = notes

    
    if len(notes_to_slur) > 1:
        slur = spanner.Slur(notes_to_slur)
        bass_line.insert(0, slur)
    piece.insert(0, chordified)
    piece.insert(0, bass_line)
    # bass_line.show('lily')
    # bass_line.show()

    # fname = bass_line.write('lily')
    # print(fname)
    # bass_line.show()
    
    return lilypond_response(piece)

def make_clef_nice(part):
    best_clef = clef.bestClef(part, recurse=True)
    part.clef = best_clef
    for measure in part.recurse().getElementsByClass('Measure'):
        measure.clef = best_clef
    for voice in part.recurse().getElementsByClass('Voice'):
        voice.clef = best_clef

def load_pretty_score(piece):
    original = corpus.parse(piece)
    imploded = original.implode()
    for part in imploded.parts:
        make_clef_nice(part)
    return imploded

def pretty_chordify(piece):
    chordified = piece.chordify(addTies=False)
    # chordified = chordified.stripTies()

    # Get rid of all the existing ties.
    chords = list(chordified.recurse().getElementsByClass('Chord'))
    for chord in chords:
        chord.closedPosition(inPlace=True)
    
    # First extract the bass line.
    bass_line = stream.Part(id='ChBass')
    chordified.id = 'Chordified'
    bass_line.partName = 'Ch. Bass'
    chordified.partName = 'Chords'
    bass_line.partName = 'Ch. Bass'
    chordified.partName = 'Chords'

    # bass_line.makeNotation(refStreamOrTimeRange=piece, inPlace=True)
    for chord in chords:
        bass_note = chord.bass()
        to_append = music21.note.Note(bass_note.nameWithOctave)
        to_append.duration = chord.duration
        bass_line.append(to_append)
    make_clef_nice(bass_line)
    bass_line.makeNotation(refStreamOrTimeRange=piece, inPlace=True)

    # Now simplify the chord harmony by reducing to a set.
    min_note = music21.note.Note('A4')
    for chord in chords:
        for note in chord:
            note.octave = 4
            if note < min_note:
                note.octave = 5
    return (chordified, bass_line)

# def bass_notes_of_measure(measure):
#     chords = measure.recurse().getElementsByClass('Chord')
#     pitch_scale = lambda note: note.pitch.ps
#     return [min(chord, key=pitch_scale) for chord in chords]
#     # return list(chords)

def group_sizes(grouping):
    result = [1]
    for grouped in grouping:
        if grouped:
            result[-1] += 1
        else:
            result.append(1)
    return result

def print_groups(grouping):
    groups = group_sizes(grouping)
    print(f'Found {len(groups)} groups:')
    for group in groups:
        print(f'  {group}')

pclass_to_number_dict = {
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
    'A': 9,
    'B': 11
}

def submod12(a, b):
    result = a - b
    if result >= 0:
        return result
    else:
        return result + 12

def addmod12(a, b):
    result = a + b
    if result < 12:
        return result
    else:
        return result - 12

def pclass_to_number(pclass):
    result = pclass_to_number_dict[pclass[0]]
    for modifier in pclass[1:]:
        if modifier == '#':
            result = addmod12(result, 1)
        elif modifier == 'b' or modifier == '-':
            result = submod12(result, 1)
        else:
            raise Exception(f'Unknown pitch class {pclass}')
    return result

# def to_triad(chord_pnums):
#     sorted_nums = sorted(list(chord_pnums))
#     first = sorted_nums[0]
#     second = sorted_nums[1]
#     third = sorted_nums[2]
#     # Root must either be first or third.
#     # root(first) -> fifth(third) /\ third(second)
#     # root(third) -> fifth(second) /\ third(first)
#     if third - first == 7:
#         if (second - first) in possible_thirds:
#             return (first, second, third)
#         else:
#             return None
#     elif submod12(second, third) == 7:
#         if submod12(first, third) in possible_thirds:
#             return (third, first, second)
#         else:
#             return None

possible_thirds = [3, 4]
def thirds_of_chord(chord):
    chord_pnums = set()
    for note in chord:
        chord_pnums.add(pclass_to_number(note.name))
    # now check every combination of pitch classes to find thirds
    result = []
    for note1, note2 in combinations(chord_pnums, 2):
        if submod12(note1, note2) in possible_thirds:
            result.append((note1, note2))
        elif submod12(note2, note1) in possible_thirds:
            result.append((note2, note1))
    return result

# Computes the jaccard similarity between the sets of pairs of thirds of the chords.
def triads_distance(chord1, chord2):
    chord1 = set(thirds_of_chord(chord1))
    chord2 = set(thirds_of_chord(chord2))
    if len(chord1) == 0 and len(chord2) == 0:
        return 0
    return 1 - len(chord1 & chord2) / len(chord1 | chord2)

def iter_window_pairs(iterable):
    it = iter(iterable)
    try:
        last_ele = next(it)
        while True:
            next_ele = next(it)
            yield (last_ele, next_ele)
            last_ele = next_ele
    except StopIteration:
        pass

def div_ceil(a, b):
    result = a / b
    if result * b == a:
        return result
    else:
        return result + 1

def analyze_piece(chordified, overlap=.3, min_dist=0.35):
    chord_measure = lambda chord: chord.measureNumber
    chords_of_piece = chordified.recurse().getElementsByClass('Chord')
    measures = [list(chords) for m, chords in groupby(chords_of_piece, key=chord_measure)]

    result = []
    for m1, m2 in iter_window_pairs(measures):
        measure_distance = chord_measure(m2[0]) - chord_measure(m1[0])
        if measure_distance <= 0:
            raise Exception('Grouping was incorrect!')
        elif measure_distance > 1:
            # If we have a gap due to rests, make sure not to group.
            for _ in range(measure_distance):
                result.append(False)
            break
        last_half = m1[int((1 - overlap) * len(m1)):]
        first_half = m2[:int(ceil(overlap * len(m2)))]
        group_measures = False
        for chord1 in last_half:
            for chord2 in first_half:
                if triads_distance(chord1, chord2) <= min_dist:
                    group_measures = True
                    break
            else:
                continue # pattern to break out of nested loop.
            break
        result.append(group_measures)
    return result
