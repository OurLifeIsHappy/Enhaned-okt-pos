# Import (lib)
from konlpy.tag import Kkma, Komoran, Okt, Hannanum
import json
from tqdm import tqdm
from kiwipiepy import Kiwi


global list_restored_word, tuple_save, kiwi_result
okt = Okt()
kiwi = Kiwi()
kiwi.prepare()
list_restored_word = []
kiwi_result = []
tuple_save=[]
noun_dict = {}
del_words = []

temp = 'None'

PATH = 'data/NXDP1902103231.json'


# function
def read_text(text='경기 양평군의회 의원들이 4대강 사업으로 철거위기에 내몰린 팔당 두물머리 유기농지를 “유기농민과 정부안이 절충돼 상생모델로 되살리자”는 내용의 ‘경기도 양평 유기농 상생대안 모델 수용 건의문’을 국토해양부와 농림수산식품부, 경기도에 냈다.'):
    return text


def save_dict_in_json(PATH_WRITE_dict,dict_result):
    with open(PATH_WRITE_dict, 'a', encoding = 'utf-8') as make_file:
        json.dump(dict_result, make_file, indent = '\t',  ensure_ascii = False)


def eliminate_single_words(words_dict):
    """
    1글자 단어 지우기
    """
    for word in words_dict:
        if len(word) == 1:
            #지울 단어 리스트
            del_words.append(word)
    # 명사사전에 남아있는 지워야할 단어 찾아서 제거
    for del_word in del_words:
        del words_dict[del_word]
    return words_dict


def compare_kiwi_okt(tuple_save):
    """
    okt가 명사로 태그하지 못한 것, kiwi로 명사 태그
    """
    global temp
    for okt_word in tuple_save:
        for kiwi_word in kiwi_result:
            if okt_word == kiwi_word:
                noun_dict[okt_word] = "Noun"
            elif str(temp+okt_word) == kiwi_word:
                noun_dict[str(temp+okt_word)] = "Noun"
        temp = okt_word


def pos_okt(text):
    """
    okt가 잘 태그하는 품사는 제외하기 위하여
    okt가 잘 태그하는 품사에 해당하는 token을 tuple_save에 따로 저장
    """
    text_pos = okt.pos(text)
    print(text_pos)
    for tuple in text_pos:
        tuple_save.append(tuple[0])
        if tuple[1] == "Josa" or tuple[1] == "Verb" or tuple[1] == "Adverb" or tuple[1] == "Adjective" or tuple[1] == "Exclamation" or tuple[1] == "Punctuation" or tuple[1] == "Foreign":
            if tuple[0] in kiwi_result:
                pass
            else:
                tuple_save.pop(-1)
    return tuple_save


def noun_kiwi(text):
    """
    kiwi가 명사로 분리한 것, 전역변수 kiwi_result에 저장
    """
    text_pos = kiwi.analyze(text)
    for index,tokens in enumerate(text_pos[0]):
        if index % 2 == 0:
            for token in tokens:
                if 'NN' in token[1] or 'NP' in token[1] or 'NR' in token[1]:
                    kiwi_result.append(token[0])


def extract_text(json_dict_data):
    """
    문장 추출 및 kiwi,okt 분석
    """
    global start_index, tuple_save, kiwi_result
    start_index = 0
    documents = json_dict_data.get("document")
    for document in tqdm(documents[start_index:], leave = True):
        sentences = document.get("sentence")
        for sentence in sentences:
            kiwi_result = []
            tuple_save=[]
            text_input = sentence.get("form")
            noun_kiwi(text_input)
            tuple_save = pos_okt(text_input)
            compare_kiwi_okt(tuple_save)


def load_json(file_name):
    with open(file_name, 'r',encoding = 'utf-8') as f:
        json_val = ''.join(f.readlines())
        json_dict_data = json.loads(json_val)
    return json_dict_data

    
if __name__ == '__main__':
    #키위로 명사사전 만들기
    #국립국어원 데이터셋 로드
    json_dict_data = load_json('data/NXDP1902103231.json')
    #국립국어원 문장추출(추출 뒤 kiwi분석포함)
    extract_text(json_dict_data)
    noun_dict = eliminate_single_words(noun_dict)
    save_dict_in_json('kiwi_okt_noun_dict.json',noun_dict)