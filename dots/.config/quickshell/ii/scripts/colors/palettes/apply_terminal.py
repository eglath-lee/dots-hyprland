#!/usr/bin/env python3
# Render the terminal themes (kitty + generic sequences) from an official
# palette instead of matugen's generated material_colours.scss.
#
# generate_colors_material.py always harmonizes the term colors toward the
# accent, so the "exact" fixed themes patch the output after generation using
# the committed catppuccin-*-terminal.json + catppuccin-*.json values.
#
# usage: apply_terminal.py <term.json> <palette.json> <template_dir> <out_dir>
import json
import sys
import re
import os


def camel(k):
    parts = k.split('_')
    return parts[0] + ''.join(x.capitalize() for x in parts[1:])


def main():
    if len(sys.argv) != 5:
        print('usage: apply_terminal.py <term.json> <palette.json> <template_dir> <out_dir>',
              file=sys.stderr)
        return 1

    term_file, palette_file, template_dir, out_dir = sys.argv[1:5]
    term = json.load(open(term_file))
    palette = json.load(open(palette_file))

    # token map: term0..term15 plus every material role (snake_case and camel)
    tokens = dict(term)
    for k, v in palette.items():
        tokens[k] = v
        if '_' in k:
            tokens[camel(k)] = v

    def substitute(text):
        def repl(m):
            val = tokens.get(m.group(1))
            return val.lstrip('#') if val is not None else '$' + m.group(1) + ' #'
        text = re.sub(r'\$([A-Za-z0-9_]+) #', repl, text)
        return text.replace('$alpha', '100')

    for name in ('kitty-theme.conf', 'sequences.txt'):
        src = os.path.join(template_dir, name)
        if not os.path.isfile(src):
            continue
        with open(src) as f:
            text = f.read()
        with open(os.path.join(out_dir, name), 'w') as f:
            f.write(substitute(text))

    return 0


if __name__ == '__main__':
    sys.exit(main())
