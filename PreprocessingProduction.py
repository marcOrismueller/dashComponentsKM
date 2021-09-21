import re
import io
import glob
import os
import json
from time import sleep
import ast
from apps.fnc_container import crud_op_db, helpers

def final_process_header(x):
    return re.sub(r'[()]', '', x).replace(' Tisch:', '')

def final_process_body(x):
    return x.replace('…', '')


def read_files(folderPath='./samples', lastFileReaded=None):
    card_header_list = []
    card_body_list = []

    for ext in ('*.100001', '*.100003', '*.100058', '*.100005'):
        available_files = glob.glob(os.path.join(folderPath, ext))
        for path_file in available_files:
            if lastFileReaded is None or float(os.path.getmtime(path_file)) > lastFileReaded:
                print(float(os.path.getmtime(path_file)))
                f = open(path_file, "rb")
                raw = json.dumps(f.read().decode(errors='replace'))
    
                regex_one = r"(?:(?:VL)|(?:B\\u000f))(\\u([a-z]+|000\d))+((\$[A-Z])|(\$\d)|(\$)| |(?:\#[^A-Z ])|\\u[0-9a-z]+)*([a-zA-Z0-9 \/\-:\.\+\,#&]+(?:(?:(?:(?:(?:\\u[a-zA-Z]+)? ?\(\d* ?[a-zA-Z.]+\) *\\ufffd)|\\ufffd(?:[A-Za-z]*)?)|(?:(?:(?:\$2\$L\$G)|(?:\$G\$2\$L\\u0000L\$G))\\u0000(?:\\ufffd[a-zA-Z]?)?[A-Za-z]*(?:\(?\d* ?[a-zA-Z.]+\)?)? *\\ufffd)|(?:\([^()]*\)))? ?[0-9\.\/ ,+]*)?)"
                raw = re.split(r"\w* ?(?:Zusammenfassung|Total)", raw)[0]
    
                matches = re.finditer(regex_one, raw, re.MULTILINE)
                text = ""
    
                for match_num, match in enumerate(matches, start=1):
                    if len(match.groups()) == 7:
                        line = f"{match.group(7)}\n"
                        if len(line) > 1:
                            text += line
    
                regex = r"(^#COPY$)|(^E$)|(^e$)|(^\d+$)|(Nr.:\d+)|(^\-[A-Z][a-z]{2,10}\-\d{2} \d{2}:\d{2})|(^: (\d|\d{2}|\d{3}))|( …)|(^\. Gang)|(\d+ Total .*)|(^\+(?=[A-Z]))"
    
                text = re.sub(regex, "", text, flags=re.MULTILINE)
    
                text = re.sub(r"(?:\$2\$L\$G\\u0000)|(?: ##)", " ", text, flags=re.MULTILINE)
                text = re.sub(r"\$G\$2\$L\\u0000L\$G\\u0000", "", text, flags=re.MULTILINE)
                text = re.sub(r"\\ufffdhnchen", "ähnchen", text, flags=re.MULTILINE)
                text = re.sub(r"Hirschpl\\ufffdttli", "Hirschplättli", text, flags=re.MULTILINE)
                text = re.sub(r"K\\ufffdse", "Käse", text, flags=re.MULTILINE)
                text = re.sub(r"K\\ufffdCHE", "KÜCHE", text, flags=re.MULTILINE)
                text = re.sub(r"Au\\ufffder", "AUSSER", text, flags=re.MULTILINE)
                text = re.sub(r"\bHaus\b", "HAUS", text, flags=re.MULTILINE)
                text = re.sub(r"\\ufffdC", "øC", text, flags=re.MULTILINE)
                text = re.sub(r"\\ufffdse", "se", text, flags=re.MULTILINE)
                text = re.sub(r"\\ufffd", "…", text, flags=re.MULTILINE)
                text = re.sub(r"(?:\n(?:^.$)?)+", "\n", text, flags=re.MULTILINE)
                text = re.sub(r"[^\S\n]+", " ", text, flags=re.MULTILINE)
                text = re.sub(r"(?:^ )|(?: $)", "", text, flags=re.MULTILINE)
                text = re.sub(r"^((?:.(?!…[\d\.\/ ]+))+)\n(.+)(…[\d\.\/ ]+)\n(.*)(\w+) (…[\d\.\/ ]+)\n\5 …[\d\.\/ ]+", r"\1 \3\n\2\6\n\4", text, flags=re.MULTILINE)
                text = re.sub(r"\bähnchen", "Hähnchen", text, flags=re.MULTILINE)
                text = re.sub(r"Wok-Gemse", "Wok-Gemüse", text, flags=re.MULTILINE)
                text = re.sub(r"Lieferdienste", "+ Lieferdienste", text, flags=re.MULTILINE)
                text = re.sub(r" …[\d\.\/ ]+\n…[\d\.\/ ]+", "", text, flags=re.MULTILINE)
                text = re.sub(r"\n", " ", text, flags=re.MULTILINE)
    
                text = re.sub(r"([A-Z]+ +)(?:\1)+", r"\1", text, flags=re.MULTILINE)
                parts = re.split(r'(?:(?<=\:\s\d\d\d)\s+|(?<=\:\s\d\d)\s+|(?<=\:\s\d)\s+|(?<=.)\s(?=[A-Z\s]+\d{1,2}x\b)|(?<=.)\s(?=\d{1,2}x\b))', text, maxsplit=1)
    
                parts[0] = parts[0].lstrip().rstrip()
                parts[1] = parts[1].lstrip().rstrip()
    
                card_header_list.append(parts[0])
                card_body_list.append(parts[1])
        
    return card_header_list, card_body_list


card_header_list, card_body_list = read_files('./samples', lastFileReaded=0.1154182)

card_header_list = [final_process_header(x) for x in card_header_list]
card_body_list = [final_process_body(x) for x in card_body_list]

listgroup_values = ast.literal_eval(str(card_body_list))
cards_headers = ast.literal_eval(str(card_header_list))

new_cards_values = helpers.extract_informations(listgroup_values, cards_headers)


card_body_list

0%120
