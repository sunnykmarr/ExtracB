# Open Issues:
# 1. Column names is assumed to be of word length 1
# 2. Values in columns is assumed to be word length 1

import nltk
import json
import pandas as pd
from flask import Flask, request
from flask_cors import CORS
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize


nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')

app = Flask(__name__)
CORS(app)

inp_file_df = None
help_strings = []
updated_inp_file_df = None
flag_df_changed = False


def preprocessing_input_file():
    global inp_file_df
    # Taking input file and finding column names
    excel_file = "Item_price.xlsx"
    inp_file_df = pd.read_excel(excel_file)


preprocessing_input_file()


def initializing_bot():
    global inp_file_df, help_strings
    print(inp_file_df.columns.values.tolist())
    # example_col=["item", "date", "price"]
    example_col_temp = []
    example_col = inp_file_df.columns.values.tolist()
    for i in range(0, len(example_col)):
        example_col_temp.append(example_col[i].lower())
    example_col = example_col_temp
    inp_file_df.columns = example_col

    help_strings.append("Hello, How I can assist you. We have file uploaded where following column names are present")
    help_strings.append(" ".join(example_col))
    help_strings.append("Please use only these column names. Here are the example queries")
    help_strings.append("1. What was the price of item cold coffee on date 25th Feb")
    help_strings.append("To stop bot please give input: Thanks. I am done.")
    return 0


def data_normalization(example_sent):
    example_sent = example_sent.replace("on","date")
    newStopWords = {"give", "me", "tell", "show", "?", "all", ',', '.'}
    stop_words = set(stopwords.words("english"))
    stop_words = stop_words.union(newStopWords)
    word_tokens = word_tokenize(example_sent)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    filtered_sentence = []
    # removing stop words and applying lemmitization
    lemmatizer = WordNetLemmatizer()
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(lemmatizer.lemmatize(w))
    # print("word tokens are", word_tokens)
    # print("filtered sentence tokens are", filtered_sentence)
    return filtered_sentence


@app.route("/")
def running_bot():
    global inp_file_df, help_strings
    global updated_inp_file_df
    global flag_df_changed
    # print("example columns are", example_col)
    # Taking user query.
    # example_sent = "give me the price of item cold coffee on date 25th feb"
    msg = request.args.get("msg")
    msg = msg.lower()
    msg = msg.strip('.')
    if msg == "yes":
        flag_df_changed = True
        return "Please provide the query"
    if msg == "help":
        return json.dumps({"type": "array", "value": help_strings})
    if not flag_df_changed:
        updated_inp_file_df = inp_file_df

    flag_df_changed = False

    example_col = updated_inp_file_df.columns
    print("Processing message: {}".format(msg))
    filtered_sentence = data_normalization(msg)
    # print("filtered sentence is", filtered_sentence)

    flag = False
    for i in range(0, len(filtered_sentence)):
        if filtered_sentence[i] not in example_col:
            i += 1
        else:
            flag = True
            break

    if not flag:
        res = "Given columns not found in input file. Please provide correct column names"
        print(res)

    allowed_operations = ["range", "sum", "maximum", "minimum", "average"]
    operation = -1
    for j in range(0, len(allowed_operations)):
        if allowed_operations[j] in filtered_sentence[0:i]:
            operation = j

    # print("i value is", i)
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
                temp_value = ""
            temp_key = filtered_sentence[i]
        elif flag:
            temp_value = temp_value + " " + filtered_sentence[i]
        i += 1

    x[temp_key.strip()] = temp_value.strip()
    # print("x value is", x)

    # df.loc[df['column_name'] == some_value]
    # print(updated_inp_file_df.head())
    query_output = updated_inp_file_df
    for i in x.keys():
        query_output = query_output[query_output[i] == x[i]]
    # query_output = inp_file_df[inp_file_df['item'] == "Cold Coffee"]

    if operation == -1:
        if len(query_output) == 0:
            query_output_string = "No data found for the query"
        elif len(query_output) == 1:
            query_output_string = query_output[
                y].head(1).to_string(index=False)
        else:
            query_output_string = "There are " + str(
                len(query_output)) + " matching rows found based on your query."
            more_query_string = "Do you want to apply more query on these rows. Type yes/no."
            print(more_query_string)
            query_output_string += "\n" + more_query_string
            updated_inp_file_df = query_output

        print(query_output_string)
        res = query_output_string
    elif operation == 0:
        try:
            res = str(query_output[y].min()) + " to " + str(query_output[y].max())
        except:
            res = "Range operation is not allowed on non numeric data. Please run the different query."
    elif operation == 1:
        try:
            res = str(query_output[y].sum())
        except:
            res = "Sum operation is not allowed on non numeric data. Please run the different query."
    elif operation == 2:
        try:
            res = str(query_output[y].max())
        except:
            res = "Max operation is not allowed on non numeric data. Please run the different query."
    elif operation == 3:
        try:
            res = str(query_output[y].min())
        except:
            res = "Min operation is not allowed on non numeric data. Please run the different query."
    else:
        try:
            res = str(query_output[y].mean())
        except:
            res = "Average operation is not allowed on non numeric data. Please run the different query."
    print(res)
    return res


# adding_stop_words()

initializing_bot()

app.run()
# running_bot(inp_file_df)
# wave_obj = sa.WaveObject.from_wave_file(get_speech(speech_txt))
# play_obj = wave_obj.play()
# play_obj.wait_done()
# print(y)
# print(x)
