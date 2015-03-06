# Copyright (c) 2015 Lapis Lazuli Texts
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

""" Program module for Pinyin text formatting. """


import getopt
import io
import re
import signal
import sys
import unicodedata


USAGE = """Usage: pinyin-dec [options] [string ...]

Decorate Pinyin text with its proper diacritics.

Options:
  -h, --help       print this help message and exit
  -v, --verbose    include information useful for debugging

"""

SEARCH_REGEX = re.compile(
    r"[aeiouüvAEIOUÜV]+(:|r|n|ng|R|N|NG)*\d(?!\d)")

PINYIN_TABLE = [
    ['ā', 'ē', 'ī', 'ō', 'ū', 'ǖ', 'Ā', 'Ē', 'Ī', 'Ō', 'Ū', 'Ǖ'],
    ['á', 'é', 'í', 'ó', 'ú', 'ǘ', 'Á', 'É', 'Í', 'Ó', 'Ú', 'Ǘ'],
    ['ǎ', 'ě', 'ǐ', 'ǒ', 'ǔ', 'ǚ', 'Ǎ', 'Ě', 'Ǐ', 'Ǒ', 'Ǔ', 'Ǚ'],
    ['à', 'è', 'ì', 'ò', 'ù', 'ǜ', 'À', 'È', 'Ì', 'Ò', 'Ù', 'Ǜ'],
    ['a', 'e', 'i', 'o', 'u', 'ü', 'A', 'E', 'I', 'O', 'U', 'Ü']]


def set_stdio_utf8():
    """
    Set standard I/O streams to UTF-8.

    Attempt to reassign standard I/O streams to new streams using UTF-8.
    Standard input should discard any leading BOM. If an error is raised,
    assume the environment is inflexible but correct (IDLE).

    """
    try:
        sys.stdin = io.TextIOWrapper(
            sys.stdin.detach(), encoding='utf-8-sig', line_buffering=True)
        sys.stdout = io.TextIOWrapper(
            sys.stdout.detach(), encoding='utf-8', line_buffering=True)
        sys.stderr = io.TextIOWrapper(
            sys.stderr.detach(), encoding='utf-8', line_buffering=True)
    except io.UnsupportedOperation:
        pass


def find_pinyin_word(text, start_idx=0):
    """
    Find the next part of a Pinyin word in a string.

    Given some arbitrary string, try to find the next relevant part of a
    word in Pinyin. If no words can be found, just return None. Since this
    function uses a special regular expression that only knows about the
    vowel(s) in a Pinyin word and the consonants and digits following it,
    only the relevant part of the Pinyin word is identified. A tuple with
    (start, end) is returned upon success.

    """
    match = SEARCH_REGEX.search(text, start_idx)
    if match:
        return match.span()
    return None


def tone_number(word):
    """
    From a numbered Pinyin word, determine the tone number.

    Given a word numbered with the Pinyin tone number, return the number
    for the tone. If there is no number attached to the word, then just
    assume the fifth tone, since that has no diacritic and is unmarked.

    """
    if word[-1] >= '0' and word[-1] <= '5':
        return int(word[-1])
    return 5


def word_nucleus(word):
    """
    Find the nucleus for a word in Pinyin.

    The basic rule for finding the nucleus of a word in Pinyin is that if
    the word contains A / E / OU, then we know the answer automatically.
    If none of those are present, then just find the last vowel. This
    function returns the nucleus character.

    """
    key = [
        ('a', 'a'), ('A', 'A'), ('e', 'e'), ('E', 'E'), ('ou', 'o'),
        ('OU', 'O'), ('Ou', 'O'), ('oU', 'o')]
    for a, b in key:
        if a in word:
            return b
    for i in range(len(word)-1, -1, -1):
        if word[i] in 'aeiouüvAEIOUÜV':
            return word[i]
    return None


def fix_pinyin_word(word):
    """
    Given a numbered Pinyin word, update it with proper diacritics.

    Given a string representing a word in Pinyin, this function tries to
    format the string using proper Pinyin tone marks. To do this, it looks
    at the tone number accompanying the word (e.g. "zhong1"), finds the
    word's nucleus, and then formats the word as Pinyin with tone marks.

    """
    word = word.replace('V', 'Ü').replace('U:', 'Ü')
    word = word.replace('v', 'ü').replace('u:', 'ü')
    if word[-1] == '0' or word[-1] == '5':
        return word[:-1]
    elif word[-1] < '0' or word[-1] > '5':
        return word
    nucleus = word_nucleus(word)
    tone = tone_number(word)
    word = word[:-1]
    if nucleus is None:
        word += 'i'
        nucleus = 'i'
    index = PINYIN_TABLE[4].index(nucleus)
    tone_char = PINYIN_TABLE[tone-1][index]
    left, _, right = word.rpartition(nucleus)
    return ''.join((left, tone_char, right))


def fix_pinyin(pinyin_str):
    """
    Format CJK words in a string as pinyin with diacritics.

    Return Pinyin words with proper diacritics, converted from words with
    tone numbers. This function will try to find Pinyin words in the text
    and then format them using proper diacritics. The input text can be
    Pinyin mixed with other text, and the search function will skip over
    anything that does not look similar to numbered Pinyin.

    """
    word_span = find_pinyin_word(pinyin_str)
    while word_span:
        left = pinyin_str[:word_span[0]]
        word = fix_pinyin_word(pinyin_str[word_span[0]:word_span[1]])
        right = pinyin_str[word_span[1]:]
        pinyin_str = left + word + right
        word_span = find_pinyin_word(pinyin_str, len(left) + len(word))
    return pinyin_str


def main(argv):
    """
    Run as a portable command-line program.

    This program will attempt to handle data through standard I/O streams
    as UTF-8 text. Input text will have a leading byte-order mark stripped
    out if one is found. Broken pipes and SIGINT are handled silently.

    """
    set_stdio_utf8()
    if 'SIGPIPE' in dir(signal):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    try:
        verbose = False
        opts, args = getopt.getopt(argv[1:], 'hv', ['help', 'verbose'])
        for option, _ in opts:
            if option in ('-h', '--help'):
                print(USAGE, end='')
                return 0
            if option in ('-v', '--verbose'):
                verbose = True
        if len(args) == 0:
            for line in sys.stdin:
                sys.stdout.write(fix_pinyin(line))
        else:
            input_str = ' '.join(args)
            print(fix_pinyin(unicodedata.normalize('NFC', input_str)))
        return 0
    except KeyboardInterrupt:
        print()
        return 1
    except Exception as err:
        if verbose:
            raise
        else:
            sys.stderr.write('pinyin-dec: ' + str(err) + '\n')
            return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
