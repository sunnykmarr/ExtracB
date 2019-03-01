# Open Issues:
# 1. Column names is assumed to be of word length 1
# 2. Values in columns is assumed to be word length 1

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd
import os, requests, time
from xml.etree import ElementTree
import simpleaudio as sa
import azure.cognitiveservices.speech as speechsdk

from flask import Flask, request
from flask_cors import CORS

speech_key, service_region = "588aa80d706d4b869a85543562160a3a", "westus"
speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config)

def create_speech():
    print("Say something...")
    result = speech_recognizer.recognize_once()
    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized: {}".format(result.text))
    elif result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech could be recognized: {}".format(result.no_match_details))
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print("Speech Recognition canceled: {}".format(cancellation_details.reason))
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print("Error details: {}".format(cancellation_details.error_details))

    return format(result.text).lower()


def get_speech(speech_txt):
    access_token = None
    tts = speech_txt
    timestr = time.strftime("%Y%m%d-%H%M")
    fetch_token_url = "https://westus.api.cognitive.microsoft.com/sts/v1.0/issueToken"
    headers = {"Ocp-Apim-Subscription-Key": speech_key}
    response = requests.post(fetch_token_url, headers=headers)
    access_token = str(response.text)

    base_url = "https://westus.tts.speech.microsoft.com/"
    path = "cognitiveservices/v1"
    constructed_url = base_url + path
    headers = {
        "Authorization": "Bearer " + str(access_token),
        "Content-Type": "application/ssml+xml",
        "X-Microsoft-OutputFormat": "riff-24khz-16bit-mono-pcm",
        "User-Agent": "YOUR_RESOURCE_NAME",
    }
    xml_body = ElementTree.Element("speak", version="1.0")
    xml_body.set("{http://www.w3.org/XML/1998/namespace}lang", "en-us")
    voice = ElementTree.SubElement(xml_body, "voice")
    voice.set("{http://www.w3.org/XML/1998/namespace}lang", "en-US")
    voice.set("name", "Microsoft Server Speech Text to Speech Voice (en-US, Guy24KRUS)")
    voice.text = tts
    body = ElementTree.tostring(xml_body)
    response = requests.post(constructed_url, headers=headers, data=body)
    if response.status_code == 200:
        with open("sample-" + timestr + ".wav", "wb") as audio:
            audio.write(response.content)
            print(
                "\nStatus code: "
                + str(response.status_code)
                + "\nYour TTS is ready for playback.\n"
            )
            global audio_name
            audio_name = str("sample-" + timestr + ".wav")
            print(audio_name)

    else:
        print(
            "\nStatus code: "
            + str(response.status_code)
            + "\nSomething went wrong. Check your subscription key and headers.\n"
        )

    return audio_name


def preprocessing_input_file():
    # Taking input file and finding column names
    excel_file = "Item_price.xlsx"
    inp_file_df = pd.read_excel(excel_file)
    return inp_file_df


def initializing_bot(inp_file_df):
    print(inp_file_df.columns.values.tolist())
    # example_col=["item", "date", "price"]
    example_col_temp = []
    example_col = inp_file_df.columns.values.tolist()
    for i in range(0, len(example_col)):
        example_col_temp.append(example_col[i].lower())
    example_col = example_col_temp
    inp_file_df.columns = example_col

    print(
        "Hello, How I can assist you. We have file uploaded where following column names are present"
    )
    example_col_string = " ".join(example_col)
    print(example_col_string)
    print("Please use only these column names. Here are the example queries")
    print("1. What was the price of item cold coffee on date 25th Feb")
    print("To stop bot please give input: Thanks. I am done.")
    return 0


def data_normalization(inp_file_df, example_sent):
    newStopWords = {"give", "me", "tell", "show", "?"}
    stop_words = set(stopwords.words("english"))
    stop_words = stop_words.union(newStopWords)
    word_tokens = word_tokenize(example_sent)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    filtered_sentence = []
    # removing stop words
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    print("word tokens are", word_tokens)
    print("filtered sentence tokens are", filtered_sentence)
    return filtered_sentence

@app.route("/")
def running_bot(inp_file_df):
    while 1:
        example_col = inp_file_df.columns
        # Taking user query.
        # example_sent = "give me the price of item cold coffee on date 25th feb"
        msg = request.args.get("msg")
        if msg is None:
            inp = input("Do you want Typing? yes/ no")
            if inp == "yes":
                msg = input("Enter the input")
            else:
                msg = create_speech()
        filtered_sentence = data_normalization(inp_file_df, msg)

        flag = False
        for i in range(0, len(filtered_sentence)):
            if filtered_sentence[i] not in example_col:
                i += 1
            else:
                flag = True
                break

        if not flag:
            print(
                "Given columns not found in input file. Please provide correct column names"
            )
            break

        allowed_operations = ["range", "sum", "maximum", "minimum", "average"]
        operation = -1
        for j in range(0, len(allowed_operations)):
            if allowed_operations[j] in filtered_sentence[0:i]:
                operation = j

        y = filtered_sentence[i]
        x = {}
        j = i + 1
        temp_key = ""
        temp_value = ""
        flag = False
        for i in range(j, len(filtered_sentence)):
            if filtered_sentence[i] in example_col:
                flag = True
                if temp_value:
                    x[temp_key.strip()] = temp_value.strip()
                    temp_key = ""
                    temp_value = ""
                temp_key = filtered_sentence[i]
            elif flag:
                temp_value = temp_value + " " + filtered_sentence[i]
            i += 1

        x[temp_key.strip()] = temp_value.strip()
        print("x value is", x)

        # df.loc[df['column_name'] == some_value]
        print(inp_file_df.head())
        query_output = inp_file_df
        for i in x.keys():
            query_output = query_output[query_output[i] == x[i]]
        # query_output = inp_file_df[inp_file_df['item'] == "Cold Coffee"]

        if operation == -1:
            print(
                "There are",
                len(query_output),
                "matching rows found based on your query",
            )
            # print(query_output, row.names = FALSE)
            print("Query output is", query_output[y].head(1).to_string(index=False))

            inp = "no"
            if len(query_output) > 1:
                print(
                    "Do you want to apply more query on these",
                    len(query_output),
                    "rows. Type yes/no",
                )
                inp = input()
                inp_file_df = query_output
            if inp != "yes":
                break
        elif operation == 0:
            try:
                print(query_output[y].min(), " to ", query_output[y].max())
            except:
                print(
                    "Range operation is not allowed on non numeric data. Please run the different query"
                )
            break
        elif operation == 1:
            try:
                print(query_output[y].sum())
            except:
                print(
                    "Sum operation is not allowed on non numeric data. Please run the different query"
                )
            break
        elif operation == 2:
            try:
                print(query_output[y].max())
            except:
                print(
                    "Max operation is not allowed on non numeric data. Please run the different query"
                )
            break
        elif operation == 3:
            try:
                print(query_output[y].min())
            except:
                print(
                    "Min operation is not allowed on non numeric data. Please run the different query"
                )
            break
        else:
            try:
                print(query_output[y].mean())
            except:
                print(
                    "Average operation is not allowed on non numeric data. Please run the different query"
                )
            break
    return 0

app = Flask(__name__)
CORS(app)

# adding_stop_words()
inp_file_df = preprocessing_input_file()
initializing_bot(inp_file_df)
running_bot(inp_file_df)
# wave_obj = sa.WaveObject.from_wave_file(get_speech(speech_txt))
# play_obj = wave_obj.play()
# play_obj.wait_done()
# print(y)
# print(x)

