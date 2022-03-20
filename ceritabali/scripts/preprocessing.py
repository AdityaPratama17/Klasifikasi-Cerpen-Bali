from tkinter.tix import Tree
from ceritabali.BahasBali.Stemmer.StemmerFactory import StemmerFactory
from ceritabali.BahasBali.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from ceritabali.models import Document, Term, TF
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string, re, os, random

def preprocessing():
    Document.objects.all().delete()
    Term.objects.all().delete()
    TF.objects.all().delete()
    factory = StopWordRemoverFactory()
    stopword = factory.create_stop_word_remover()
    factory2 = StemmerFactory()
    stemmer = factory2.create_stemmer()

    terms,id_doc,id_tf = preprocessing_test(stopword,stemmer)
    preprocessing_train(stopword,stemmer,terms,id_doc,id_tf)

def preprocessing_test(stopword,stemmer):
    all_files = os.listdir("static/Data Cerpen/Data Testing")
    terms = {}
    id_tf = 1
    for id,name_file in enumerate(all_files):
        # READ DOCUMENTS
        file = open("static/Data Cerpen/Data Testing/"+name_file,"r")
        doc_raw = file.readlines()
        file.close()
        
        # GET DOCUMENT INFO
        ket = doc_raw[0].split("|")
        docs = ket[1].replace("\n", "") + " "
        doc_db = ''
        for paragraf in doc_raw[2:]:
            docs += paragraf.replace("\n", "")
            paragraf = paragraf.replace('Ã©', '&eacute').replace('Ã¨', '&eacute').replace("\n", "")
            doc_db += paragraf + '|'

        # INSERT DOC TO DB
        Document.objects.create(
            id = id+1,
            judul = ket[1].replace("\n", ""),
            doc = doc_db,
            kelas = ket[0].replace("ï»¿", "").lower(),
            fold = 0,
            tipe = 'test',
        )
        
        # PREPROCESSING
        # -- case folding
        tokens = docs.lower()
        # -- remove angka
        tokens = re.sub(r"\d+", "", tokens)
        #remove punctuation
        tokens = tokens.translate(str.maketrans("","",string.punctuation))
        #remove whitespace leading & trailing
        tokens = tokens.strip()
        #remove multiple whitespace into single whitespace
        tokens = re.sub('\s+',' ',tokens)
        # -- normalization
        tokens = tokens.replace('ã©', 'e').replace('ã¨', 'e').replace('ï¿½', 'e')
        # -- filetering
        tokens = stopword.remove(tokens)
        # -- stemming
        tokens = stemmer.stem(tokens)
        # -- tokenisasi
        tokens = word_tokenize(tokens)

        # UNIQUE TERM & TERM FREQUENCY (TF)
        unique_terms = list(set(tokens))
        for term in unique_terms:
            if term not in terms:
                # INSERT TERM TO DB
                Term.objects.create(
                    id = len(terms)+1,
                    term = term,
                )
                terms[term] = {}

            # INSERT TF TO DB
            TF.objects.create(
                id = id_tf,
                id_doc = id+1,
                term = term,
                tf = tokens.count(term),
            )
            id_tf+=1
        
        print(id+1,'.','test : ',ket[1].replace("\n", ""))

    return terms,len(all_files)+1,id_tf

def preprocessing_train(stopword,stemmer,terms,id_doc,id_tf):
    all_files = os.listdir("static/Data Cerpen/Data Training")
    all_files = random.sample(all_files, len(all_files))
    kelas_train = {
        '1' : {'anak':1,'remaja':1,'dewasa':1},
        '2' : {'anak':1,'remaja':1,'dewasa':1},
        '3' : {'anak':1,'remaja':1,'dewasa':1},
    }
    for id,name_file in enumerate(all_files):
        # READ DOCUMENTS
        file = open("static/Data Cerpen/Data Training/"+name_file,"r")
        doc_raw = file.readlines()
        file.close()

        # GET DOCUMENT INFO
        ket = doc_raw[0].split("|")
        docs = ket[1].replace("\n", "") + " "
        doc_db = ''
        for paragraf in doc_raw[2:]:
            docs += paragraf.replace("\n", "")
            paragraf = paragraf.replace('Ã©', '&eacute').replace('Ã¨', '&eacute').replace("\n", "")
            doc_db += paragraf + '|'

        # SPLIT FOLD
        kelas = ket[0].replace("ï»¿", "").lower()
        flag = ''
        for i in kelas_train:
            if kelas == 'anak':
                if i == '1':
                    if kelas_train[i]['anak'] <= 14:
                        flag = kelas
                else:
                    if kelas_train[i]['anak'] <= 13:
                        flag = kelas
            if kelas == 'remaja':
                if i == '2':
                    if kelas_train[i]['remaja'] <= 14:
                        flag = kelas
                else:
                    if kelas_train[i]['remaja'] <= 13:
                        flag = kelas
            if kelas == 'dewasa':
                if i == '3':
                    if kelas_train[i]['dewasa'] <= 14:
                        flag = kelas
                else:
                    if kelas_train[i]['dewasa'] <= 13:
                        flag = kelas
            if flag != '':
                fold = int(i)
                kelas_train[i][flag] += 1
                break

        # INSERT DOC TO DB
        Document.objects.create(
            id = id_doc,
            judul = ket[1].replace("\n", ""),
            doc = doc_db,
            kelas = kelas,
            fold = fold,
            tipe = 'train',
        )

        # PREPROCESSING
        # -- case folding
        tokens = docs.lower()
        # -- remove angka
        tokens = re.sub(r"\d+", "", tokens)
        #remove punctuation
        tokens = tokens.translate(str.maketrans("","",string.punctuation))
        #remove whitespace leading & trailing
        tokens = tokens.strip()
        #remove multiple whitespace into single whitespace
        tokens = re.sub('\s+',' ',tokens)
        # -- normalization
        tokens = tokens.replace('ã©', 'e').replace('ã¨', 'e').replace('ï¿½', 'e')
        # -- filetering
        tokens = stopword.remove(tokens)
        # -- stemming
        tokens = stemmer.stem(tokens)
        # -- tokenisasi
        tokens = word_tokenize(tokens)

        # UNIQUE TERM & TERM FREQUENCY (TF)
        unique_terms = list(set(tokens))
        for term in unique_terms:
            if term not in terms:
                # INSERT TERM TO DB
                Term.objects.create(
                    id = len(terms)+1,
                    term = term,
                )
                terms[term] = {}

            # INSERT TF TO DB
            TF.objects.create(
                id = id_tf,
                id_doc = id_doc,
                term = term,
                tf = tokens.count(term),
            )
            id_tf+=1
        print(id_doc,'.','train : ',ket[1].replace("\n", ""))
        id_doc += 1

def get_data():
    docs_db = Document.objects.filter().values()
    docs = {}
    for i,doc in enumerate(docs_db):
        docs[i+1] = doc
        docs[i+1]['term'] = []
    
    term_db = Term.objects.filter().values()
    terms = {}
    for term in term_db:
        terms[term['term']] = {}
    
    tf_db = TF.objects.filter().values()
    for value in tf_db:
        terms[value['term']][value['id_doc']] = value['tf']
        docs[value['id_doc']]['term'].append(value['term']) 
    
    return docs,terms