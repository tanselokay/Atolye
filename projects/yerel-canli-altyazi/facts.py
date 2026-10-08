# Generated with Claude (Anthropic). Review before use.
# Bu dosya Claude (Anthropic) ile üretilmiştir; kullanmadan önce gözden geçirin.
"""Days and times that must survive translation unchanged.

A translation may rephrase anything except the facts a meeting runs on. The
27B turned "bis Mittwoch, 16 Uhr" into "Salı günü saat 16.00" - Wednesday into
Tuesday - and the notes then reported Tuesday as a deadline. Asking the model to
be careful does not make it careful, so this is checked in code: weekday names
map to the same day in every language, and clock numbers are compared as
numbers. Standard library only.
"""

import re

# Longest first within a language, so "cumartesi" is not read as "cuma" and
# "pazartesi" not as "pazar". Matched as word PREFIXES: Turkish adds suffixes
# ("perşembeye") and German compounds ("Mittwochmittag").
WEEKDAYS = {
    "tr": ["pazartesi", "salı", "çarşamba", "perşembe", "cumartesi", "cuma", "pazar"],
    "de": ["montag", "dienstag", "mittwoch", "donnerstag", "freitag", "samstag", "sonntag"],
    "en": ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"],
}
_DAY = {"pazartesi": 0, "salı": 1, "çarşamba": 2, "perşembe": 3, "cuma": 4,
        "cumartesi": 5, "pazar": 6}
for _names in (WEEKDAYS["de"], WEEKDAYS["en"]):
    _DAY.update({name: i for i, name in enumerate(_names)})
_NAMES = sorted(_DAY, key=len, reverse=True)

# Days named relative to today. qwen3.8 rendered "wir hatten Donnerstag gesagt"
# as "DÜN Perşembe demiştik" - a yesterday nobody said. Turkish forms are listed
# whole, not matched as prefixes: "dün" starts "dünya", and "yarın" is close to
# "yarım". German "morgen" counts only in lower case: "Morgen" is the morning.
RELATIVE = {
    "dün": -1, "dünkü": -1, "dünden": -1, "dünü": -1,
    "bugün": 0, "bugünkü": 0, "bugüne": 0, "bugünden": 0,
    "yarın": 1, "yarınki": 1, "yarına": 1, "yarından": 1,
    "gestern": -1, "vorgestern": -2, "heute": 0, "übermorgen": 2,
    "yesterday": -1, "today": 0, "tomorrow": 1,
}

_NUMBER = re.compile(r"(?<![\d.:])(\d{1,2})(?:[:.]\d{2})?(?![\d])")

# Numbers written as words. Whisper small wrote "sabah ONA kadar" (10) and NLLB
# turned it into "Donnerstag früh" - the ten o'clock vanished and the digit
# check saw nothing. One is left out in every language: "bir", "ein" and "one"
# are mostly articles.
_TR_UNITS = {"iki": 2, "üç": 3, "dört": 4, "dörd": 4, "beş": 5, "altı": 6,
             "yedi": 7, "sekiz": 8, "dokuz": 9}
_TR_TENS = {"on": 10, "yirmi": 20, "otuz": 30, "kırk": 40, "elli": 50}
# Only these endings make a number a number: "altıda" is at six, "altında" is
# under. "dörd" is "dört" before a vowel ("dörde").
_TR_ENDINGS = {"", "a", "e", "ya", "ye", "da", "de", "ta", "te", "dan", "den",
               "tan", "ten", "ı", "i", "u", "ü", "yı", "yi"}
# "ona", "onda", "onu" are also "to him", "at him", "him". After a time word
# they are ten; anywhere else they are not counted.
_TIME_WORDS = {"saat", "sabah", "sabahı", "akşam", "akşamı", "öğlen", "öğle",
               "gece", "gecesi"}
_UNITS = {
    "de": ["zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun"],
    "en": ["two", "three", "four", "five", "six", "seven", "eight", "nine"],
}
_WORDS = {}
for _lang, _units in _UNITS.items():
    _WORDS.update({w: i + 2 for i, w in enumerate(_units)})
_WORDS.update({"zehn": 10, "elf": 11, "zwölf": 12, "dreizehn": 13, "vierzehn": 14,
               "fünfzehn": 15, "sechzehn": 16, "siebzehn": 17, "achtzehn": 18,
               "neunzehn": 19, "zwanzig": 20, "einundzwanzig": 21,
               "zweiundzwanzig": 22, "dreiundzwanzig": 23, "vierundzwanzig": 24,
               "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
               "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
               "eighteen": 18, "nineteen": 19})
_EN_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50}


def _tr_value(word, table):
    for base in sorted(table, key=len, reverse=True):
        if word.startswith(base) and word[len(base):] in _TR_ENDINGS:
            return table[base]
    return None


def _word_numbers(text):
    found, words = set(), re.findall(r"\w+", _lower(text))
    for i, word in enumerate(words):
        before = words[i - 1] if i else ""
        after = words[i + 1] if i + 1 < len(words) else ""
        if word in _WORDS:
            found.add(_WORDS[word])
        elif word in _EN_TENS:
            unit = _WORDS.get(after, 0)
            found.add(_EN_TENS[word] + unit if unit < 10 else _EN_TENS[word])
        elif (tens := _tr_value(word, _TR_TENS)) is not None:
            unit = _tr_value(after, _TR_UNITS) if word in _TR_TENS else None
            if unit:
                found.add(tens + unit)                     # "on dörtte" = 14
            elif tens != 10 or word == "on" or before in _TIME_WORDS:
                found.add(tens)
        elif (unit := _tr_value(word, _TR_UNITS)) is not None:
            if before not in _TR_TENS:          # else already counted as "on dört"
                found.add(unit)
    return found


# Parts of the day are times too. Aya wrote "Mittwochvormittag" (Wednesday
# morning) for "çarşamba öğlene" (Wednesday noon) - the weekday survived, the
# time did not. 0 morning, 1 noon, 2 afternoon, 3 evening, 4 night.
_PARTS_TR = [("öğleden sonra", 2), ("öğleden önce", 0), ("sabah", 0), ("öğle", 1),
             ("akşam", 3), ("gece", 4)]
_PARTS_DE = {"vormittag": 0, "morgen": 0, "mittag": 1, "nachmittag": 2,
             "abend": 3, "nacht": 4}
_PARTS_EN = {"morning": 0, "noon": 1, "midday": 1, "afternoon": 2,
             "evening": 3, "night": 4}


def parts(text):
    """Morning / noon / afternoon / evening / night in `text`, as 0-4."""
    found, low = set(), _lower(text)
    for phrase, part in _PARTS_TR:
        for match in re.finditer(r"\b" + phrase, low):
            found.add(part)
            low = low[:match.start()] + " " * len(phrase) + low[match.end():]
    words = [(i, w) for sentence in re.split(r"[.!?]+", text)
             for i, w in enumerate(re.findall(r"\w+", sentence))]
    for i, word in words:
        stem = _lower(word)
        for name in _NAMES:                  # "Donnerstagmorgen" -> "morgen"
            if stem.startswith(name) and len(stem) > len(name):
                stem = stem[len(name):]
                break
        stem = stem[:-1] if stem.endswith("s") and stem[:-1] in _PARTS_DE else stem
        if stem in _PARTS_EN:
            found.add(_PARTS_EN[stem])
        elif stem in _PARTS_DE:
            # Bare "morgen" / sentence-initial "Morgen" is tomorrow - see relative().
            if _lower(word) == "morgen" and (word == "morgen" or i == 0):
                continue
            found.add(_PARTS_DE[stem])
    return found


def _lower(text):
    # Turkish has two i's; str.lower() gets both wrong.
    return text.replace("İ", "i").replace("I", "ı").lower()


def days(text):
    """The weekdays named in `text`, as numbers (Monday = 0), any language."""
    found = set()
    for word in re.findall(r"\w+", _lower(text)):
        for name in _NAMES:
            if word.startswith(name):
                found.add(_DAY[name])
                break
    return found


def relative(text):
    """Yesterday / today / tomorrow and kin in `text`, as offsets from today."""
    found = set()
    for sentence in re.split(r"[.!?]+", text):
        for i, word in enumerate(re.findall(r"\w+", sentence)):
            # "morgen" is tomorrow; "Morgen" is the morning - except as the first
            # word of a sentence, where it is tomorrow again ("Morgen beginnen wir").
            if word == "morgen" or (word == "Morgen" and i == 0):
                found.add(1)
            elif _lower(word) in RELATIVE:
                found.add(RELATIVE[_lower(word)])
    return found



def numbers(text):
    """Numbers in `text`, as digits or words: "16:00", "16 Uhr", "on altı" are all 16."""
    return {int(n) for n in _NUMBER.findall(text)} | _word_numbers(text)


def same(original, translation):
    """True when the translation names the same days, times and numbers as the original."""
    said, got = parts(original), parts(translation)
    # A part of the day may not change or appear from nowhere. It may be dropped
    # only while a clock time still carries it: "perşembe sabah 10'a" ->
    # "Donnerstag, 10 Uhr" keeps the fact; "çarşamba öğlene" -> "Mittwoch" does not.
    parts_kept = got <= said and (said <= got or bool(numbers(original)))
    return (days(original) == days(translation)
            and relative(original) == relative(translation)
            and parts_kept
            and numbers(original) == numbers(translation))


_BACK = set("aıou")


def _last_vowel_back(word):
    vowels = [c for c in word if c in "aıoueiöü"]
    return bool(vowels) and vowels[-1] in _BACK


def repair(original, translation, target):
    """Put the right weekday back when it is the ONLY thing the translation got wrong.

    The 27B wrote "Salı" for "Mittwoch" three times in three, even when told
    the answer - asking does not fix it, but the original says which day it is.
    Only a single, swapped day is repaired, and only where the Turkish suffix
    still fits the new word (vowel harmony); anything else returns None.
    """
    said, got = days(original), days(translation)
    names = WEEKDAYS.get(target)
    if not names or len(said) != 1 or len(got) != 1 or said == got:
        return None
    if numbers(original) != numbers(translation):
        return None
    right = next(n for n in names if _DAY[n] == next(iter(said)))
    wrong = next(n for n in names if _DAY[n] == next(iter(got)))

    def swap(match):
        word = match.group(0)
        if not _lower(word).startswith(wrong):
            return word
        rest = word[len(wrong):]
        if rest and target == "tr" and _last_vowel_back(wrong) != _last_vowel_back(right):
            raise ValueError("suffix would no longer fit")
        new = right.capitalize() if word[0].isupper() else right
        return new + rest

    try:
        fixed = re.sub(r"\w+", swap, translation)
    except ValueError:
        return None
    return fixed if same(original, fixed) else None


_SPOKEN = {0: "sıfır", 1: "bir", 2: "iki", 3: "üç", 4: "dört", 5: "beş", 6: "altı",
           7: "yedi", 8: "sekiz", 9: "dokuz", 10: "on", 20: "yirmi"}
_CASES = {"e": "dat", "a": "dat", "ye": "dat", "ya": "dat",
          "de": "loc", "da": "loc", "te": "loc", "ta": "loc",
          "den": "abl", "dan": "abl", "ten": "abl", "tan": "abl"}


def _suffix(number, case):
    """The Turkish case ending for a numeral, as it is read aloud: 16'ya, 14'te, 10'dan."""
    last = _SPOKEN[number % 10] if number % 10 else _SPOKEN[number]
    back = _last_vowel_back(last)
    if case == "dat":
        return ("y" if last[-1] in "aıoueiöü" else "") + ("a" if back else "e")
    hard = last[-1] in "çfhkpsşt"
    return ("t" if hard else "d") + ("a" if back else "e") + ("n" if case == "abl" else "")


def repair_clock(original, translation, target):
    """Turn a 12-hour time back into the 24-hour time that was said.

    NLLB rendered "bis Mittwoch, 16 Uhr" as "çarşamba günü 4'e kadar" - the
    hour on a 12-hour clock - and the line was withheld, so a key deadline had
    no translation on screen. When the ONLY numeric difference is n for n+12,
    the original says which it is: put 16 back, and regenerate the Turkish
    ending for the new numeral (4'e -> 16'ya), since endings follow the number
    as it is read. Returns the patched text, or None if this is not that case.
    """
    said, got = numbers(original), numbers(translation)
    extra, missing = got - said, said - got
    if len(extra) != 1 or len(missing) != 1:
        return None
    wrong, right = next(iter(extra)), next(iter(missing))
    if not (1 <= wrong <= 11 and right == wrong + 12):
        return None

    def swap(match):
        digits, minutes, ending = match.group(1), match.group(2) or "", match.group(3) or ""
        if int(digits) != wrong:
            return match.group(0)
        case = _CASES.get(ending[1:].lower()) if ending else None
        if target == "tr" and ending and case is None:
            raise ValueError("an ending we cannot regenerate")
        new_ending = "'" + _suffix(right, case) if (target == "tr" and case) else ending
        return f"{right}{minutes}{new_ending}"

    try:
        return re.sub(r"(?<![\d.:])(\d{1,2})([:.]\d{2})?('[^\W\d_]+)?", swap, translation)
    except ValueError:
        return None


def checked(translate, fallback=None):
    """Wrap a translator so a line whose days or numbers change never reaches the screen.

    The translator goes first. If it only read a time on a 12-hour clock or
    swapped a weekday, repair_clock() / repair() put the said one back. Otherwise the fallback (NLLB, literal and measured right on every
    weekday here) gets one try. If that moves a fact too, the line is shown
    untranslated: an original alone is incomplete, a wrong day is a false record.
    """
    def run(text, src, target, context=None):
        # Context (earlier lines) only reaches the main translator; the fallback
        # is a literal model that takes one sentence at a time.
        first = translate(text, src, target, context) if context else translate(text, src, target)
        if same(text, first):
            return first
        # A 12-hour time first, then a swapped weekday - either can be repaired
        # from the original alone; both together as well.
        clock = repair_clock(text, first, target) or first
        fixed = clock if same(text, clock) else repair(text, clock, target)
        if fixed:
            print(f"[facts] repaired from the original: {first!r} -> {fixed!r}",
                  flush=True)
            return fixed
        if fallback:
            try:
                second = fallback(text, src, target)
                if same(text, second):
                    print(f"[facts] LLM changed a day/number, used fallback: {text!r}",
                          flush=True)
                    return second
            except Exception as failed:     # noqa: BLE001 - never break the stream
                print(f"[facts] fallback failed ({failed})", flush=True)
        print(f"[facts] no translation kept the days/numbers, showing original only: "
              f"{text!r} -> {first!r}", flush=True)
        return ""

    return run


def unsaid(notes, originals):
    """Words for days and times, and numbers, in `notes` that no original line contains."""
    said_days, said_relative, said_parts, said_numbers = set(), set(), set(), set()
    for line in originals:
        said_days |= days(line)
        said_relative |= relative(line)
        said_parts |= parts(line)
        said_numbers |= numbers(line)
    words = [w for w in re.findall(r"\w+", notes)
             if days(w) - said_days or relative(w) - said_relative]
    words += [name for name, part in _PARTS_TR if part in parts(notes) - said_parts]
    return sorted(set(words)), sorted(numbers(notes) - said_numbers)
