# main.py
"""프로그램 실행 파일"""
# Import (lib)
import json
from tqdm import tqdm
from konlpy.tag import Okt
from typing import List
import time


def get_json_data(file_name):
    """
    dictionary를 포함하는 Json format의 파일을 불러옴.
    """
    with open(file_name, 'r',encoding = 'utf-8') as f:
        json_val = ''.join(f.readlines())
        json_dict_data = json.loads(json_val)
    return json_dict_data


okt = Okt()
change = {}
#config 파일 Load
config = get_json_data('data/res/config.json')
PATH_DATASET = config.get("PATH_DATASET")
PATH_NOUN_DICT = config.get("PATH_NOUN_DICT")
noun_dict = get_json_data(PATH_NOUN_DICT)
PATH_WRITE_dict = config.get("PATH_WRITE_dict")
start_index = config.get("start_index")
end_index = config.get("end_index")


class Result():
    list_result:list = []
    def __init__(self):
        self.list_result = []
        pass
global_result = Result()


class Changed():
    list_changed:list=[]
    def __init__(self):
        self.listchanged =[]
        pass
global_changed = Changed()


def save_change_log(change):
    """
    딕셔너리에 저장된 이력 파일로 변환
    """
    with open(PATH_WRITE_dict, 'a', encoding = 'utf-8') as make_file:
        json.dump(change, make_file, indent = '\t',  ensure_ascii = False)   


def change_log(form_sentence):
    """
    변경 이력 딕셔너리에 저장
    """
    change[form_sentence] = f"품사 태그{global_result.list_result}\n 명사로 바뀐 oktpos : {global_changed.list_changed} "


def change_pos(tokens):
    """
    품사 교체
    """
    # (제,modifier) (작,modifier) 같은 문제를 해결하기 위해
    # ("Josa", "Verb", "Adverb", "Adjective", "Exclamation", "Punctuation", "Foreign")에 해당하지 않고
    # 사전에서 발견되지 않은 단어를 
    # 다음 for문에서 합치기 위해 임시로 저장하는 변수
    temp = ""
    # 개선된 품사 태그 결과가 담기는 리스트
    global_result.list_result = []
    # 어떤 단어의 품사가 변경되었는지 확인할 수 있도록 변경 이력을 담는 리스트
    global_changed.list_changed = []
    for token in tokens:
        text, pos = token
        #품사 태그 결과를 저장
        global_result.list_result.append([text,pos])
        
        
        # 한국어 LR구조를 이용하여 Josa, Verb 왼쪽에 위치한 word를 명사로 추정
        

        # Okt가 잘 태그하고, 명사사전으로 태그를 바꾸기 곤란한, 품사(Josa, Verb, Adverb, Adjective, Exclamation, Punctuation, Foreign)를 제외
        if pos in ("Josa", "Verb", "Adverb", "Adjective", "Exclamation", "Punctuation", "Foreign"):
            temp = ""
            continue
        # Okt가 형태소 단위로 쪼갠 Token이 명사사전에 있으면 태그 결과 리스트에서 해당 토큰 품사를 명사로 변경
        if text in noun_dict:
            global_result.list_result[-1][-1] = "Noun"
            #Okt Pos가 태그한 품사가 원래 명사였으면 변경기록에 남기지 않음
            if pos == "Noun":
                temp = ""
                continue
            global_changed.list_changed.append(f"[{text},{pos}] -> [{text},Noun]")
            temp = ""
        # 명사사전의 단어와 일치하지 않아 저장되어있는 이전 for문의 token을 현재 for문의 token과 합침
        # (제,modifier) (작,modifier) 의 경우 이전 for문에서의 '제'가 temp에 담겨, 현재 for문의 '작'과 합쳐져 '제작'이 됨.
        elif str(temp+text) in noun_dict:
            global_result.list_result.pop()
            global_result.list_result.append([str(temp+text),"Noun"])
            global_changed.list_changed.append(f"[{str(temp+text)},multi-pos] -> [{str(temp+text)},Noun]")
            temp = ""
        # 위 조건에 해당하지 않으면 제대로 된 단어가 아니기 때문에 다음 for문에서 추가하려고 결과리스트에서 token을 삭제.
        # 명사사전이 충분하지 않으면 오류확률 증가.
        else:
            global_result.list_result.pop()
            temp = temp + text #previous

        
def okt_pos(form_sentence):
    """
    OKT 토크나이징
    """
    tokens: list = okt.pos(form_sentence)
    return tokens
    


def tour_sentences(sentences: List[str]):
    """
    문장 리스트 순회하여 검사할 문장 호출
    """
    for sentence in sentences:
        tokens = okt_pos(sentence)
        change_pos(tokens)
        change_log(sentence)
    save_change_log(change)

def extract_sentence(json_dict_data) -> List[str]:
    """
    raw data로부터 문장 리스트 반환
    """
    #추출된 문장 담을 리스트
    sentences = list()
    #국립국어원 Dataset 구조 : document -> sentence -> form(문장)
    documents = json_dict_data.get("document")
    for document in tqdm(documents[start_index:], leave = True):
        #국립국어원 Dataset [sentence]리스트
        sentences_dict = document.get("sentence")
        for sentence in sentences_dict:
            #국립국어원 Dataset [form]리스트
            form_sentence = sentence.get("form")
            #국립국어원 Dataset에서 추출한 문장 리스트
            sentences.append(form_sentence)
    return sentences

if __name__ == '__main__':
    # 국립국어원 데이터셋
    json_dict_dataset = get_json_data(PATH_DATASET)
    sentences = extract_sentence(json_dict_dataset)
    tour_sentences(sentences)
