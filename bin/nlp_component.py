# Open Issues:
# 1. Column names is assumed to be of word length 1
# 2. Values in columns is assumed to be word length 1

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pandas as pd

# Taking input file and finding column names
excel_file = '../Item_price.xlsx'
inp_file_df = pd.read_excel(excel_file)
print(inp_file_df.columns.values.tolist())
#example_col=["item", "date", "price"]
example_col_temp = []
example_col = inp_file_df.columns.values.tolist()
for i in range(0, len(example_col)):
    example_col_temp.append(example_col[i].lower())
example_col = example_col_temp
inp_file_df.columns = example_col

print("Column names present in the list are:")
example_col_string=" ".join(example_col)
print(example_col_string)

#print ("Hello, How am I hell you")

while(1):
    # Taking user query.
    #example_sent = "What was the price of item cold coffee on date 25th feb"
    example_sent=input("Enter the input")
    stop_words = set(stopwords.words('english'))
    word_tokens = word_tokenize(example_sent)
    filtered_sentence = [w for w in word_tokens if not w in stop_words]
    filtered_sentence = []
    for w in word_tokens:
        if w not in stop_words:
            filtered_sentence.append(w)
    print("word tokens are", word_tokens)
    print("filtered sentence tokens are", filtered_sentence)

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

    y=filtered_sentence[i]
    x={}
    j=i+1

    temp_key= ""
    temp_value = ""
    for i in range(j, len(filtered_sentence)):
        if filtered_sentence[i] in example_col:
            if(temp_value):
                x[temp_key.strip()]=temp_value.strip()
                temp_key = ""
                temp_value = ""
            temp_key=filtered_sentence[i]
        else:
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
    print("There are", len(query_output), "matching rows found based on your query")
    #print(query_output, row.names = FALSE)
    print("Query output is", query_output[y].head(1))
    inp='no'
    if(len(query_output) > 1):
        print("Do you want to apply more query on these", len(query_output), "rows")
        inp = input()
        inp_file_df=query_output
    if(inp!='yes'):
        break

#print(y)
#print(x)