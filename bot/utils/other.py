from string import ascii_uppercase
import random, shutil, os


def random_string(length):
    return "".join(random.choices(ascii_uppercase, k=length))


def reset_directory():
    try:
        shutil.rmtree("files")
    except:
        pass
    try:
        os.mkdir("files")
    except:
        pass


def create_directory(name):
    try:
        os.mkdir(f"files/{name}")
    except:
        pass


def get_file_size(file_path: str) -> int:
    return os.path.getsize(file_path)


def break_list(data: list, size: int):
    new_data = []
    result = []

    for i in data:
        new_data.append(i)
        if len(new_data) == size:
            result.append(new_data)
            new_data = []

    if len(new_data) > 0:
        try:
            result[-1].extend(new_data)
        except IndexError:
            result.append(new_data)

    return result
