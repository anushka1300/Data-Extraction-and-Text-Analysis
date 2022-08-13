import pandas as pd
import requests
from bs4 import BeautifulSoup
import os, re
from nltk.tokenize import word_tokenize, sent_tokenize
from SyllableAndPronounsCount import sylco, countPronouns

df = pd.read_excel('excel files\\Input.xlsx')
urls = df.URL
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
for index, url in enumerate(urls):
    page = requests.get(url, headers=headers).text
    soup = BeautifulSoup(page, "html.parser")
    containers = soup.find_all("p")
    with open(f'textFiles/{index+1}.txt', 'w', encoding='utf-8') as f:
        f.write(soup.title.string)
        f.write("\n")
        for container in containers:
            f.write(container.get_text())
            f.write("\n")
    print("success",index+1)

stopWordspath = "stopWords"
os.chdir(stopWordspath)
with open('allStopWords.txt','w') as outfile:
    for file in os.listdir():
        with open(file) as infile:
            for line in infile:
                outfile.write(line)

os.chdir('..')

# SENTIMENTAL ANALYSIS
delete_list = open("stopWords/allStopWords.txt").read()
positive_words_list = open("positive-words.txt").read()
negative_words_list = open("negative-words.txt").read()

# all stop words are deleted
path2 = "textFiles"
os.chdir(path2)
cleaned_words = []
for index, file in enumerate(os.listdir()):
    fin = open(file, encoding='utf-8').read()
    fin2 = re.sub('[^a-zA-Z0-9\n\.]', ' ', fin)
    token = word_tokenize(fin2)
    results_cleaned_words = [i for i in token if not i in delete_list]
    cleaned_words.append(len(results_cleaned_words))
    os.chdir('..')
    with open(f'cleanedTextfile/{index + 1}.txt', 'w') as fout:
        for result in results_cleaned_words:
            fout.write(result)
            fout.write(" ")
    os.chdir(path2)

os.chdir('..')

# finding positive and negative words count
path3 = "cleanedTextfile"
os.chdir(path3)
positive_Score =[]
negative_Score =[]
polarity_score =[]
for index2, file in enumerate(os.listdir()):
    string = open(file).read()
    token = word_tokenize(string)
    results_positive = [i for i in token if i in positive_words_list]
    results_negative = [i for i in token if i in negative_words_list]
    results_polarity = (len(results_positive)-len(results_negative))/((len(results_positive)+len(results_negative))+0.000001)
    positive_Score.append(len(results_positive))
    negative_Score.append(len(results_negative))
    polarity_score.append(results_polarity)

# print(len(cleaned_words))
# print(len(positive_Score))
# print(len(negative_Score))
# calculating subjectivity score
subjectivity_score = []
for i in range(len(positive_Score)):
    subjectivity_score.append((positive_Score[i]+negative_Score[i])/(cleaned_words[i]+0.000001))

os.chdir('..')

# ANALYSIS OF READABILITY
# Average sentence length
os.chdir(path2)
total_words = []
total_sentences = []
complex_words = []
total_syllables = []
total_pronouns = []
total_characters = []
for file in os.listdir():
    string = open(file,encoding='utf-8').read() # full text of the article along with title
    new_str = re.sub('[^a-zA-Z0-9\n\.]',' ', string) # removing all the special characters
    #removing extra spaces and periods
    string_1 = new_str.replace('   ', ' ')
    string_2 = string_1.replace('  ', ' ')
    string_3 = string_2.replace('.', '')
    string_6 = string_3.replace('\n',' ')
    token = word_tokenize(string_6)
    total_words.append(len(token))
    # determining the number of characters in the text
    string_4 = string_3.replace(' ','')
    string_5 = string_4.replace('\n','')
    total_characters.append(len(string_5))
    # determining the number of sentences in the text
    sentences = sent_tokenize(string)
    total_sentences.append(len(sentences))
    pronouns = 0
    for sentence in sentences:
        pronouns = countPronouns(sentence) + pronouns
    total_pronouns.append(pronouns)
    totalsyllablesintext=0
    complexwords = 0
    for eachword in token:
        countSyllable = sylco(eachword)
        totalsyllablesintext = totalsyllablesintext + countSyllable
        if countSyllable > 2:
            complexwords = complexwords + 1
    complex_words.append(complexwords)
    total_syllables.append(totalsyllablesintext)


#calculating average sentence length
#Percentage of complex words
average_sentence_length = []
percentage_complex_words = []
fog_index = []
syllable_count_per_word = []
average_word_length = []
for i in range(len(total_sentences)):
    average_sentence_length.append(total_words[i]/total_sentences[i])
    percentage_complex_words.append(complex_words[i] * 100 / total_words[i])
    fog_index.append(0.4*(average_sentence_length[i]+percentage_complex_words[i]))
    syllable_count_per_word.append(total_syllables[i]/total_words[i])
    average_word_length.append(total_characters[i]/total_words[i])


df['POSITIVE SCORE'] = positive_Score
df['NEGATIVE SCORE'] = negative_Score
df['POLARITY SCORE'] = polarity_score
df['SUBJECTIVITY SCORE'] = subjectivity_score
df['AVERAGE SENTENCE LENGTH'] = average_sentence_length
df['PERCENTAGE OF COMPLEX WORDS'] = percentage_complex_words
df['FOG INDEX'] = fog_index
df['AVERAGE NUMBER OF WORDS PER SENTENCE'] = average_sentence_length
df['COMPLEX WORD COUNT'] = complex_words
df['WORD COUNT'] = cleaned_words
df['SYLLABLE COUNT PER WORD'] = syllable_count_per_word # total syllables in the text/ total words in the text
df['PERSONAL PRONOUNS'] = total_pronouns
df['AVERAGE WORD LENGTH'] = average_word_length
print(df)
os.chdir('..')
df.to_excel("output.xlsx")

