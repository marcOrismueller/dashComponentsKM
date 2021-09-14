import json
import re
# https://regex101.com/r/NZkzgI/1
# https://regex101.com/r/DfoNyp/1
# https://regex101.com/r/mJzIW6/1
# https://regex101.com/r/TuMSxC/1
# https://regex101.com/r/RmDqeQ/1


def read_file():
    # path_file = "/home/hoangyell/Downloads/00002909.005.100058"
    path_file = "bons100005/00000058.001.100005"
    f = open(path_file, "rb")
    raw = json.dumps(f.read().decode(errors='replace'))
    return raw


def extract_text_from_file(raw):
    regex = r"(?:(?:VL)|(?:zB\\u000f))(\\u([a-z]+|000\d))+((\$[A-Z])|(\$\d)|(\$)| |(?:\#[^A-Z ])|\\u[0-9a-z]+)*([a-zA-Z0-9 \/\-:\.\+\,#&]+(?:(?:(?:(?:\\u[a-zA-Z]+ ?\(\d+ [a-zA-Z.]+\) *\\ufffd)|\\ufffd(?:[A-Za-z]*)?)|(?:\$2\$L\$G\\u0000[A-Za-z]*(?:\(?\d* ?[a-zA-Z.]+\)?)? *\\ufffd)|(?:\([^()]*\)))? ?[0-9\.\/ ,+]*)?)"
    raw = re.split(r"\w* ?(?:Zusammenfassung|Total)", raw)[0]
    matches = re.finditer(regex, raw, re.MULTILINE)
    text = ""
    for match_num, match in enumerate(matches, start=1):
        if len(match.groups()) == 7:
            line = f"{match.group(7)}\n"
            if len(line) > 1:
                text += line
    return text


def format_text(text):
    regex = r"(^#COPY$)|(^E$)|(^e$)|(^\d+$)|(Nr.:\d+)|(^\-[A-Z][a-z]{2,10}\-\d{2} \d{2}:\d{2})|(^: 88)|( …)|(^\. Gang)|(\d+ Total .*)|(^\+(?=[A-Z]))"
    text = re.sub(regex, "", text, flags=re.MULTILINE)
    text = re.sub(r"(?:\$2\$L\$G\\u0000)|(?: ##)", " ", text, flags=re.MULTILINE)
    text = re.sub(r"Hirschpl\\ufffdttli", "Hirschplätzli", text, flags=re.MULTILINE)
    text = re.sub(r"K\\ufffdse", "Käse", text, flags=re.MULTILINE)
    text = re.sub(r"K\\ufffdCHE", "KÜCHE", text, flags=re.MULTILINE)
    text = re.sub(r"\\ufffdC", "øC", text, flags=re.MULTILINE)
    text = re.sub(r"\\ufffdse", "se", text, flags=re.MULTILINE)
    text = re.sub(r"\\ufffd", "…", text, flags=re.MULTILINE)
    text = re.sub(r"(?:\n(?:^.$)?)+", "\n", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text, flags=re.MULTILINE)
    text = re.sub(r"(?:^ )|(?: $)", "", text, flags=re.MULTILINE)
    return text


def main():
    raw = read_file()
    text = extract_text_from_file(raw)
    formatted_text = format_text(text)
    print(formatted_text)


main()
