from netlib.filecaster import Filecaster, here
from netlib import logs
from pathlib import Path

logs.init(filepath=None)


directory = here()

read_f = Filecaster(directory, name='_color_list', ext='html', mode='r')
write_f = Filecaster(directory, name='colors', ext='json', mode='w', indent=2)

reg = {}

try:
    while True:
        line = read_f.read(raw_string=True)

        if line.startswith(r'<p><a'):
            line = line.removeprefix(r'<p><a href="')

            line = line.split('>', 1)[1]
            terms = line.split('<')

            name = terms[0].strip()

            color = terms[-1].split('>')[-1].strip()

            while name in reg:
                name = name + '+'

            reg[name] = color

except Exception as e:
    pass


write_f.cast(reg)

read_f.exit()
write_f.exit()


