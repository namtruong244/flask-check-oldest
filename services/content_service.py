import json
import os

from bs4 import BeautifulSoup
from pydub import AudioSegment
from pydub.silence import split_on_silence
import speech_recognition as sr

from models.content_model import ContentModel
from models.user_model import UserModel
from config.cmn_const import CmnConst
import requests
import string
import urllib.parse


recognizer = sr.Recognizer()


def get_all_content():
    content_model = ContentModel()
    cursor = content_model.get_all_content()

    data = []
    for record in cursor:
        data.append({
            "id": record["ID"],
            "userId": record["USER_ID"],
            "userName": record["USERNAME"],
            "fullName": record["FULLNAME"],
            "email": record["EMAIL"],
            "content": record["CONTENT"],
            "classType": record["CLASS_TYPE"],
            "languageType": record["LANGUAGE_TYPE"],
            "title": record["TITLE"]
        })

    return {"contents": data}


def create_new_content(request, current_user):
    user_model = UserModel()
    cursor = user_model.get_user_by_username_and_email(current_user)
    if cursor.rowcount == 0:
        return {"ok": False, "message": "Your account currently does not exist"}
    user = cursor.fetchone()

    content_model = ContentModel()

    content_model.begin()
    data = {
        "USER_ID": user["USER_ID"],
        "CONTENT": request["content"],
        "CLASS_TYPE": request["classType"],
        "LANGUAGE_TYPE": request["languageType"],
        "TITLE": request["title"]
    }

    content_model.insert_data(data)
    content_model.commit()

    return {"ok": True, "message": "Content created successfully!"}


def compare_text_result(request):
    content_model = ContentModel()

    # Get content by id
    column = ["CONTENT"]
    condition = {"ID": request["contentId"], "DELETE_FLG": CmnConst.DELETE_FLG_OFF}
    cursor = content_model.select_data(column, condition)
    if cursor.rowcount == 0:
        return {"ok": False, "message": "Content not found"}

    text_1_split = __normalizer_text(cursor.fetchone()["CONTENT"], is_join=False)
    text_2_split = __normalizer_text(request["textInput"], is_join=False)

    len_text_split = [len(text_1_split), len(text_2_split)]
    if len_text_split.count(0) == 0:
        len_text_split.sort()
        is_add_break_line = (len_text_split[0] / len_text_split[1]) * 100 < 37

        if is_add_break_line is True:
            if len(text_1_split) > len(text_2_split):
                text_1_split.insert(len(text_2_split), "\n")
            else:
                text_2_split.insert(len(text_1_split), "\n")

    content = __url_encoded(" ".join(text_1_split))
    text_input = __url_encoded(" ".join(text_2_split))

    # Call API compare text
    header = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8"}
    data = f"text1={content}&text2={text_input}&with_ajax=1"

    response = requests.post("https://text-compare.com/", data=data, headers=header)
    res = json.loads(response.text)
    if "comparison" in res and res["comparison"] is not None:
        soup = BeautifulSoup(res["comparison"], features="html5lib")
        trs = soup.find_all("tr")

        diff_input_1 = []
        diff_input_2 = []
        for child in trs:
            tds = child.find_all("td", {"class": "lineContent"})
            for index, td in enumerate(tds):
                result = (str(td)
                          .replace('<td class="lineContent"><pre>', '')
                          .replace('</pre></td>', '')
                          .replace('<span class="difference">', '[')
                          .replace('</span>', ']')).replace('[ ]', '').replace('[]', '')
                if index == 0:
                    diff_input_1.append(result)
                else:
                    diff_input_2.append(result)

        return {"ok": True, "data": {"isDiff": True, "text1": " ".join(diff_input_1), "text2": " ".join(diff_input_2)}}

    return {"ok": True, "data": {"isDiff": False}}


def get_text_from_speech(file_name, request):
    text_recognizer = ""
    path_file = f"{file_name}.wav"
    path_file_temp = f"{file_name}_temp"
    for audio_chunk in __load_chunks(path_file):
        audio_chunk.export(path_file_temp, format="wav")
        with sr.AudioFile(path_file_temp) as source:
            audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio, language=request["languageType"])
            except Exception:
                pass
            else:
                text_recognizer += text.lower() + " "

    text_recognizer = __normalizer_text(text_recognizer)

    if os.path.exists(path_file_temp) is True:
        os.remove(path_file_temp)

    if text_recognizer.strip() == "":
        return {"ok": False, "message": "Your audio source is very noise"}

    return {"ok": True, "text": text_recognizer}


def __load_chunks(filename):
    """
        Splitting the large audio file into chunks
        and apply speech recognition on each of these chunks
    """
    # open the audio file using pydub
    long_audio = AudioSegment.from_wav(filename)
    # split audio sound where silence is 700 milliseconds or more and get chunks
    audio_chunks = split_on_silence(
        long_audio,
        min_silence_len=500,
        silence_thresh=long_audio.dBFS-14,
        keep_silence=500
    )
    return audio_chunks


def __url_encoded(text):
    return urllib.parse.quote_plus(text)


def __normalizer_text(text, is_join=True):
    text_without_punctuation = text.translate(str.maketrans('', '', string.punctuation)).lower()
    text_split = text_without_punctuation.split()
    if is_join is True:
        return " ".join(text_split)

    return text_split


def __add_break_line(text_arr, max_item):
    new_arr = []
    for i, letter in enumerate(text_arr):
        if i % max_item == 0:
            new_arr.append('\n')
        new_arr.append(letter)

    return " ".join(new_arr[1:])
