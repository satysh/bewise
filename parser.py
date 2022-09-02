#!/usr/bin/env python3
"""
@author: Ilyas Satyshev
@phone: +79267216381
@e-mail: satyshevi@gmail.com
"""
import spacy
import pandas as pd

# simple _*100 printer
def print_underline():
    for i in range(100):
        print('_', end='')
    print('\n')

# load and def instruments
russian_nlp = spacy.load('ru_core_news_md')
keywords_for_manager_name = ['зовут', 'это']
keywords_for_greeting = ['здравствуйте', 'добрый']
keywords_for_goodbye = ['всего хорошего', 'до свидания', 'всего доброго']

# csv reading
table = pd.read_csv('test_data.csv', delimiter=',')
dlg_id_list = table['dlg_id']
line_n_list = table['line_n']
role_list   = table['role']
text_list   = table['text']

# markers creating
requirement             = dict() # [dld_id : [greeting_int, goodbye_int]]
requirement_status_list = list() # to print requirement done=True or not=False in out csv
insight_status_list     = list() # [line_i_in_table-1]=greeting/goodbye = True/False to print in out csv
## init
for dlg_id in dlg_id_list:
    requirement[dlg_id] = [0, 0]
    insight_status_list.append('')
    requirement_status_list.append('')

# print greetings and manager name condidates search
manager_name_condidates_set = set()
for i in range(len(text_list)):
    ## skip client text
    if role_list[i] == 'client':
        continue
    text = text_list[i].lower()
    word_list = text.split()
    for word in keywords_for_greeting:
        if word in word_list:
            print('greeting: ', dlg_id_list[i], line_n_list[i], role_list[i], text_list[i])
            requirement[dlg_id_list[i]][0] += 1
            insight_status_list[i] = 'greeting=True'
    spacy_parser = russian_nlp(text)
    for entity in spacy_parser.ents:
        if (entity.label_ == 'PER'):
            if len(entity) == 1:
                manager_name_condidates_set.add(str(entity))

print_underline()

# print introduce and manager name search
managers_names_set = set()
for i in range(len(text_list)):
    text = text_list[i].lower()
    word_list = text.split()
    for conditate in manager_name_condidates_set:
        if conditate in word_list:
            index = word_list.index(conditate)
            if index > 0:
                if word_list[index-1] in keywords_for_manager_name:
                    print('introduce: ', dlg_id_list[i], line_n_list[i], role_list[i], text_list[i])
                    managers_names_set.add(conditate)
                elif index < len(word_list)-2:
                    if word_list[index+1] in keywords_for_manager_name:
                        print('introduce: ', dlg_id_list[i], line_n_list[i], role_list[i], text_list[i])
                        managers_names_set.add(conditate)

print_underline()

## print manager names 
for name in managers_names_set:
    print('manager name: ', name)

print_underline()

# company names search
company_names_set = set()
for i in range(len(text_list)):
    text = text_list[i].lower()
    words_list = text.split()
    counter = 0
    answ = ''
    words_list.append(line_n_list[i])
    for word in words_list:
        if word == 'компания' and counter < len(text)-1:
            answ = words_list[counter+1]
            if counter < len(words_list)-2 and words_list[counter+2] == 'бизнес':
                answ += ' бизнес'
            if int(words_list[-1]) < 5:
                company_names_set.add(answ)
        counter+=1

## print company names
for company in company_names_set:
    print('company: ', company)

print_underline()

# print goodbye
for i in range(len(text_list)):
    ## skip client text
    if role_list[i] == 'client':
        continue
    text = text_list[i].lower()
    words_list = text.split()
    for word in keywords_for_goodbye:
        sub_words_list = word.split()
        if sub_words_list[0] in words_list and sub_words_list[1] in words_list:
            index = words_list.index(sub_words_list[1]) 
            if index > 0:
                if words_list[index-1] == sub_words_list[0]:
                    print('goodbye: ', dlg_id_list[i], line_n_list[i], role_list[i], text_list[i])
                    insight_status_list[i] = 'goodbye=True'
                    requirement[dlg_id_list[i]][1] += 1
                    break

print_underline()

# requirement check and print checking result 
counter = 0
for key, val in requirement.items():
    print('requirement: dlg_id =', key, end = ' ')
    if val[0] > 0 and val[1] > 0:
        print('True')
        requirement_status_list[counter] = f'dlg_id={key} True'
    else:
        print('False')
        requirement_status_list[counter] = f'dlg_id={key} False'
    counter += 1

print_underline()

# wrtiting out csv
new_table = pd.DataFrame(table)
new_table['insight'] = insight_status_list
new_table['requirement'] = requirement_status_list
new_table.to_csv('parsed_test_data.csv')
