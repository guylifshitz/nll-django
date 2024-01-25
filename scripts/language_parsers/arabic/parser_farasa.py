from pathlib import Path
import subprocess
import string

punctuation = list(string.punctuation) + ["؟"]


def parse_titles(titles):
    temp_folder = Path("temp/arabic/")
    temp_folder.mkdir(parents=True, exist_ok=True)

    with open(str(temp_folder) + "/raw_lines.txt", "w") as f:
        f.write("\n".join(titles))

    subprocess.call(
        [
            "java",
            "-jar",
            "language_parsers/arabic/farasa_java/farasa_processor/farasa_processor.jar",
            "temp/arabic",
        ]
    )
    subprocess.call(
        [
            "java",
            "-jar",
            "language_parsers/arabic/farasa_java/FarasaPOS/FarasaPOSJar.jar",
            "-i",
            "temp/arabic/raw_lines.txt",
            "-o",
            "temp/arabic/parsed_pos.txt",
        ]
    )
    subprocess.call(
        [
            "java",
            "-jar",
            "language_parsers/arabic/farasa_java/FarasaNER/FarasaNERJar.jar",
            "-i",
            "temp/arabic/raw_lines.txt",
            "-o",
            "temp/arabic/parsed_ner.txt",
        ]
    )

    parsed_titles_cleaned = []
    with open(str(temp_folder) + "/parsed_cleaned.txt", "r") as f:
        contents = f.read()
        parsed_titles_cleaned = [line.split(" ") for line in contents.split("\n")]

    parsed_titles_lemma = []
    with open(str(temp_folder) + "/parsed_lemma.txt", "r") as f:
        contents = f.read()
        parsed_titles_lemma = [line.split(" ") for line in contents.split("\n")]

    parsed_titles_segmented = []
    with open(str(temp_folder) + "/parsed_segmented.txt", "r") as f:
        contents = f.read()
        parsed_titles_segmented = [line.split(" ") for line in contents.split("\n")]

    parsed_titles_pos = []
    with open(str(temp_folder) + "/parsed_pos.txt", "r") as f:
        contents = f.read()
        parsed_titles_pos = handle_pos(contents, parsed_titles_lemma)

    parsed_titles_name = []
    with open(str(temp_folder) + "/parsed_ner.txt", "r") as f:
        contents = f.read()
        parsed_titles_name = [line.split(" ") for line in contents.split("\n")]
        parsed_titles_name = parsed_titles_name[:-1]
    parsed_titles_pos = set_names_on_pos(parsed_titles_pos, parsed_titles_name)

    parsed_titles_prefixes = []
    # parsed_titles_pos = []
    parsed_titles_feats = []
    print(parsed_titles_pos)

    for parsed_title in parsed_titles_cleaned:
        prefixes = [None for _ in range(len(parsed_title))]
        #         poses = [None for _ in range(len(parsed_title))]
        feats = [None for _ in range(len(parsed_title))]
        parsed_titles_prefixes.append(prefixes)
        # parsed_titles_pos.append(poses)
        parsed_titles_feats.append(feats)

    rm_tree(temp_folder)

    return (
        parsed_titles_cleaned,
        parsed_titles_lemma,
        parsed_titles_segmented,
        parsed_titles_prefixes,
        parsed_titles_pos,
        parsed_titles_feats,
    )


def handle_pos(contents, parsed_titles_lemma):
    contents = contents.split("\n")[:-1]

    parsed_pos = [cleanup_pos(line) for line in contents]
    parsed_pos = fix_wrong_pos_lemma(parsed_pos, parsed_titles_lemma)
    return parsed_pos


def cleanup_pos(pos_line):
    parsed_pos = pos_line.replace("S/S ", "").replace(" E/E ", "").split(" ")

    all_words = []

    current_word = ""
    last_pos_type = None
    for index, pos_word in enumerate(parsed_pos):
        current_word_type = check_pos_type(pos_word)
        match current_word_type:
            case "prefix":
                if last_pos_type == "prefix":
                    current_word += pos_word
                else:
                    all_words.append(current_word)
                    current_word = pos_word
            case "word":
                if last_pos_type == "prefix":
                    current_word += pos_word
                else:
                    all_words.append(current_word)
                    current_word = pos_word
            case "postfix":
                current_word += pos_word
        last_pos_type = current_word_type
    all_words.append(current_word)
    return all_words[1:]


def check_pos_type(pos_component):
    if "+/" in pos_component:
        return "prefix"
    if pos_component.startswith("+"):
        return "postfix"
    return "word"


def fix_wrong_pos_lemma(pos_lines, lemma_lines):
    lines = zip(pos_lines, lemma_lines)
    for line_index, (pos_line, lemma_line) in enumerate(lines):
        bad_line = False

        if len(pos_line) != len(lemma_line):
            bad_line = True
        else:
            for word_index, pos_word in enumerate(pos_line):
                lemma_word = lemma_line[word_index]
                if lemma_word not in pos_word:
                    bad_line = True
                    break

        if bad_line:
            print("bad line", line_index, pos_line, lemma_line)
            pos_lines[line_index] = ["---" for word in lemma_line]

    return pos_lines


def set_names_on_pos(parsed_titles_pos, parsed_titles_name):
    assert len(parsed_titles_pos) == len(parsed_titles_name)

    for line_index, ner_line in enumerate(parsed_titles_name):
        bad_line = False

        if len(ner_line) != len(parsed_titles_pos[line_index]):
            bad_line = True
        else:
            for word_index, ner_word in enumerate(ner_line):
                ner_lemma = ner_word.split("/")[0]
                ner_type = ner_word.split("/")[-1]

                if ner_type != "O":
                    if ner_lemma not in parsed_titles_pos[line_index][word_index]:
                        bad_line = True
                    else:
                        parsed_titles_pos[line_index][word_index] = (
                            parsed_titles_pos[line_index][word_index]
                            + "/NAME/"
                            + ner_type
                        )

        if bad_line:
            print("bad line", line_index, ner_line, parsed_titles_pos[line_index])
            parsed_titles_pos[line_index] = [
                "!!!" for word in parsed_titles_pos[line_index]
            ]

    return parsed_titles_pos


def rm_tree(pth):
    pth = Path(pth)
    for child in pth.glob("*"):
        if child.is_file():
            child.unlink()
        else:
            rm_tree(child)
    pth.rmdir()
