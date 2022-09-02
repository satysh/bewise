#!/usr/bin/env python3
"""
@author: Ilyas Satyshev
"""
import spacy
import pandas as pd

russian_nlp = spacy.load('ru_core_news_md')

'''
filepath = 'text.txt'
text = open(filepath, encoding='utf-8').read()
'''
keywords_for_PER = ['зовут', 'это']
keywords_for_greeting = ['здравствуйте', 'добрый']
keywords_for_goodbye = ['всего хорошего', 'до свидания', 'всего доброго']


table = pd.read_csv('test_data.csv', delimiter=',')
dlg_id_list = table['dlg_id']
line_n_list = table['line_n']
role_list = table['role']
sens_list = table['text']

insight_status_list = list()
requirement_status_list = list()
requirement = dict() # [dld_id : [2]]
for dlg_id in dlg_id_list:
    insight_status_list.append('')
    requirement_status_list.append('')
    requirement[dlg_id] = [0, 0]


PER_condidates_set = set()
#sens_list = [sens_list[i] for i in range(len(sens_list)) if role_list[i] == 'manager']
for i in range(len(sens_list)):
    text = sens_list[i].lower()
    text_list = text.split()
    for word in keywords_for_greeting:
        if word in text_list and role_list[i] == 'manager':
            print('greeting: ', dlg_id_list[i], line_n_list[i], role_list[i], sens_list[i])
            requirement[dlg_id_list[i]][0] += 1
            insight_status_list[i] = 'greeting=True'
    spacy_parser = russian_nlp(text)
    for entity in spacy_parser.ents:
        if (entity.label_ == 'PER'):
            if len(entity) == 1:
                text_list = text.split()
                index = text_list.index(str(entity))
                #print(f'Found: {entity.text} : {entity.label_} : {index} : {text}')
                PER_condidates_set.add(str(entity))

#print(PER_condidates_set)
print()
managers_names_set = set()
for i in range(len(sens_list)):
    text = sens_list[i].lower()
    text_list = text.split()
    for conditate in PER_condidates_set:
        if conditate in text_list:
            index = text_list.index(conditate)
            if index > 0:
                if text_list[index-1] in keywords_for_PER:
                    print('introduce: ', dlg_id_list[i], line_n_list[i], role_list[i], sens_list[i])
                    managers_names_set.add(conditate)
                elif index < len(text_list)-2:
                    if text_list[index+1] in keywords_for_PER:
                        print('introduce: ', dlg_id_list[i], line_n_list[i], role_list[i], sens_list[i])
                        managers_names_set.add(conditate)


print()

for name in managers_names_set:
    print('manager name: ', name)

companys_set = set()

for i in range(len(sens_list)):
    sens = sens_list[i].lower()
    words_list = sens.split()
    counter = 0
    answ = ''
    words_list.append(line_n_list[i])
    for word in words_list:
        if word == 'компания' and counter < len(sens)-1:
            answ = words_list[counter+1]
            if counter < len(words_list)-2 and words_list[counter+2] == 'бизнес':
                answ += ' бизнес'
            if int(words_list[-1]) < 5:
                companys_set.add(answ)
        counter+=1

print()

for company in companys_set:
    print('company: ', company)

print()

for i in range(len(sens_list)):
    sens = sens_list[i].lower()
    sens_sub_list = sens.split()
    for word in keywords_for_goodbye:
        words_list = word.split()
        if words_list[0] in sens_sub_list and words_list[1] in sens_sub_list:
            if abs(sens_sub_list.index(words_list[0]) - sens_sub_list.index(words_list[1])) == 1:
                print('goodbye: ', dlg_id_list[i], line_n_list[i], role_list[i], sens_list[i])
                insight_status_list[i] = 'goodbye=True'
                requirement[dlg_id_list[i]][1] += 1
                break

print()

counter = 0
for key, val in requirement.items():
    print('requirement: dlg_id=', key, end = ' ')
    if val[0] > 0 and val[1] > 0:
        print('True')
        requirement_status_list[counter] = f'dlg_id={key} True'
    else:
        print('False')
        requirement_status_list[counter] = f'dlg_id={key} False'
    counter += 1

new_table = pd.DataFrame(table)
new_table['insight'] = insight_status_list
new_table['requirement'] = requirement_status_list
new_table.to_csv('parsed_test_data.csv')
