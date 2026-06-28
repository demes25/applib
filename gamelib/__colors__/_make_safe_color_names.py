from netlib.filecaster import Filecaster, here
from netlib import logs

logs.init(filepath=None)
directory = here()

f = Filecaster(directory=directory, name='renamed_sorted_colors', ext='json', separator='!', mode='r')

dct = f.read()

f.exit()

newdct = {}

f = Filecaster(directory=directory, name='renamed_sorted_colors', ext='json', indent=2)


splitchars = [' ', '\'', '-']
def lower_take_to_underscore(name : str) -> str:
    name = name.lower()
    for char in splitchars:
        name = '_'.join(name.split(char))
    return name


def descriptor_remover(descriptor : str, replace_in_front : str):
    d = f'({descriptor})'
    def _remove(name : str) -> str:
        if d in name:
            name = name.removesuffix(d)
            name = name.removesuffix('_')
            name = replace_in_front + '_' + name
        return name

    return _remove


CURRENT = descriptor_remover('floral', 'floral')

for color, cdict in dct.items():
    k = {}

    for name, val in cdict.items():
        k[CURRENT(name)] = val
    
    dct[color] = k

f.cast(dct)
f.exit()


