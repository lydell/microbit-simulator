# NOTE: Glyphs are only implemented for a tiny subset of all letters!


NUM_ROWS = 5


blank_column = [' ' * NUM_ROWS]


_glyphs = {
    '0': (
        ' ## '
        '#  #'
        '#  #'
        '#  #'
        ' ## '
    ),
    '1': (
        ' # '
        '## '
        ' # '
        ' # '
        '###'
    ),
    '2': (
        '### '
        '   #'
        ' ## '
        '#   '
        '####'
    ),
    '3': (
        '####'
        '   #'
        '  # '
        '#  #'
        ' ## '
    ),
    '4': (
        '  ## '
        ' # # '
        '#  # '
        '#####'
        '   # '
    ),
    '5': (
        '#####'
        '#    '
        '#### '
        '    #'
        '#### '
    ),
    '6': (
        '   # '
        '  #  '
        ' ### '
        '#   #'
        ' ### '
    ),
    '7': (
        '#####'
        '   # '
        '  #  '
        ' #   '
        '#    '
    ),
    '8': (
        ' ### '
        '#   #'
        ' ### '
        '#   #'
        ' ### '
    ),
    '9': (
        ' ### '
        '#   #'
        ' ### '
        '  #  '
        ' #   '
    ),
    '?': (
        ' ### '
        '#   #'
        '  ## '
        '     '
        '  #  '
    ),
}


def _convert(glyph):
    num_columns = len(glyph) // NUM_ROWS
    columns = []

    for x in range(num_columns):
        columns.append([])

    for index, letter in enumerate(glyph):
        columns[index % num_columns].append(letter)

    return columns


glyphs = {
    letter: _convert(glyph) for letter, glyph in _glyphs.items()
}


def get_glyph(letter):
    return glyphs.get(letter, glyphs['?'])
