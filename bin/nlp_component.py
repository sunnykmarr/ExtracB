# Open Issues:
# 1. Column names is assumed to be of word length 1
# 2. Values in columns is assumed to be word length 1

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd

# Adding stop words in nltk
#def custom_stop_words(stop_words_list):
#    stop_words = stopwords.words('english')
#    print(type(stop_words))
#    newStopWords = ["give", "me", "tell", "show"]
#    stop_words.append(newStopWords[0])
#   return 0

def preprocessing_input_file():
    # Taking input file and finding column names
    excel_file = 'Item_price.xlsx'
    inp_file_df = pd.read_excel(excel_file)
    return  inp_file_df

def initializing_bot(inp_file_df):
    print(inp_file_df.columns.values.tolist())
    #example_col=["item", "date", "price"]
    example_col_temp = []
    example_col = inp_file_df.columns.values.tolist()
    for i in range(0, len(example_col)):
        example_col_temp.append(example_col[i].lower())
    example_col = example_col_temp
    inp_file_df.columns = example_col

    print("Hello, How I can assist you. We have file uploaded where following column names are present")
    example_col_string=" ".join(example_col)
    print(example_col_string)
    print ("Please use only these column names. Here are the example queries")
    print("1. What was the price of item cold coffee on date 25th Feb")
    print("To stop bot please give input: Thanks. I am done.")
    return 0

def data_normalization(inp_file_df, example_sent):
    newStopWords = {"give", "me", "tell", "show"}
    stop_words = set(stopwords.words('english'))
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

def running_bot(inp_file_df):
    while(1):
        example_col = inp_file_df.columns
        # Taking user query.
        #example_sent = "give me the price of item cold coffee on date 25th feb"
        example_sent = input("Enter the input")
        filtered_sentence = data_normalization(inp_file_df, example_sent)

        flag=False
        for i in range(0, len(filtered_sentence)):
            if filtered_sentence[i] not in example_col:
                i+=1
            else:
                flag=True
                break

        if(not flag):
            print("Given columns not found in input file. Please provide correct column names")
            break

        allowed_operations = ["range", "sum", "maximum", "minimum", "average"]
        operation=-1
        for j in range(0,len(allowed_operations)):
            if(allowed_operations[j] in filtered_sentence[0:i]):
                operation = j

        y=filtered_sentence[i]
        x={}
        j=i+1
        temp_key= ""
        temp_value = ""
        flag=False
        for i in range(j, len(filtered_sentence)):
            if filtered_sentence[i] in example_col:
                flag=True
                if(temp_value):
                    x[temp_key.strip()]=temp_value.strip()
                    temp_key = ""
                    temp_value = ""
                temp_key=filtered_sentence[i]
            elif(flag):
                temp_value=temp_value + " " + filtered_sentence[i]
            i+=1

        x[temp_key.strip()]=temp_value.strip()
        print("x value is", x)

        #df.loc[df['column_name'] == some_value]
        print(inp_file_df.head())
        query_output = inp_file_df
        for i in x.keys():
            query_output = query_output[query_output[i] == x[i]]
        #query_output = inp_file_df[inp_file_df['item'] == "Cold Coffee"]

        if(operation==-1):
            print("There are", len(query_output), "matching rows found based on your query")
            #print(query_output, row.names = FALSE)
            print("Query output is", query_output[y].head(1).to_string(index=False))

            inp='no'
            if(len(query_output) > 1):
                print("Do you want to apply more query on these", len(query_output), "rows")
                inp = input()
                inp_file_df=query_output
            if(inp!='yes'):
                break
        elif(operation==0):
            try:
                print(query_output[y].min()," to ", query_output[y].max())
            except:
                print("Range operation is not allowed on non numeric data. Please run the different query")
            break
        elif(operation==1):
            try:
                print(query_output[y].sum())
            except:
                print("Sum operation is not allowed on non numeric data. Please run the different query")
            break
        elif(operation==2):
            try:
                print(query_output[y].max())
            except:
                print("Max operation is not allowed on non numeric data. Please run the different query")
            break
        elif(operation == 3):
            try:
                print(query_output[y].min())
            except:
                print("Min operation is not allowed on non numeric data. Please run the different query")
            break
        else:
            try:
                print(query_output[y].mean())
            except:
                print("Average operation is not allowed on non numeric data. Please run the different query")
            break
    return 0


#adding_stop_words()
inp_file_df = preprocessing_input_file()
initializing_bot(inp_file_df)
running_bot(inp_file_df)
#print(y)
#print(x)