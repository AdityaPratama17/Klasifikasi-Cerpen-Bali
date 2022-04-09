from django.shortcuts import render, redirect
from .models import Document, Term, TF, Term_prob
from .komputasi.preprocessing import preprocessing, get_data
from .komputasi.naive_bayes import naive_bayes, test as testing_nb
from .komputasi.evaluasi import confusion_matrix
from .komputasi.genetic_algorithm import genetic_algorithm, evaluasi as eval_kfcv
from ceritabali.BahasBali.Stemmer.StemmerFactory import StemmerFactory
from ceritabali.BahasBali.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from nltk.tokenize import word_tokenize
import string, re

def index(request):
    return redirect('ceritabali:dokumen')

def dokumen(request):
    doc_db = Document.objects.filter().values()
    docs = []
    doc_unique = []
    for i in doc_db:
        if i['judul'] not in doc_unique:
            doc_unique.append(i['judul'])
            docs.append({'id': i['id'], 'judul': i['judul'].replace('ï¿½', '&eacute'), 'kelas':i['kelas'],'doc':i['doc'].replace("|", "")})

    context ={
        'title' : 'Dokumen',
        'docs' : docs,
    }
    return render(request, 'ceritabali/dokumen.html', context)

def detail(request, id):
    doc_db = Document.objects.filter(id=id).values()
    context ={
        'title' : 'Detail',
        'docs' : doc_db[0]['doc'].split('|'),
        'judul' : doc_db[0]['judul'].replace('ï¿½', '&eacute'),
        'kelas' : doc_db[0]['kelas'],
    }
    return render(request, 'ceritabali/detail.html', context)

def pengujian(request):
    if request.method == 'POST':
        # GET DATA
        docs,terms = get_data()
        doc_test = {}
        doc_train = {}
        terms_train = {}
        for doc in docs:
            if docs[doc]['tipe'] == 'train':
                doc_train[doc] = docs[doc]
                # GET TERMS IN DATA TRAIN
                for term in docs[doc]['term']:
                    if term not in terms_train:
                        terms_train[term] = terms[term]
            else:
                doc_test[doc] = docs[doc]
        
        # DENGAN SELEKSI FITUR
        if request.POST['seleksi'] == 'yes':
            generasi = int(request.POST['iterasi'])
            jum_kromosom = int(request.POST['kromosom'])
            pc = float(request.POST['cr'])
            pm = float(request.POST['mr'])
            model,fold = genetic_algorithm(doc_train,terms_train,generasi,jum_kromosom,len(terms_train),pc,pm)
            model = model['prob_term']

        # TANPA SELEKSI FITUR
        else:
            fold = {
                'akurasi' : {'fold-1':0,'fold-2':0,'fold-3':0,'avg':0},
                'precision' : {'fold-1':0,'fold-2':0,'fold-3':0,'avg':0},
                'recall' : {'fold-1':0,'fold-2':0,'fold-3':0,'avg':0},
                'f_measure' : {'fold-1':0,'fold-2':0,'fold-3':0,'avg':0},
            }
            for i in range(1,4):
                # GET DATA TRAIN & TEST
                doc_train_fold = {}
                doc_test_fold = {}
                terms_train_fold = {}
                for doc in doc_train:
                    if doc_train[doc]['fold'] == i:
                        doc_test_fold[doc] = doc_train[doc]
                    else:
                        doc_train_fold[doc] = doc_train[doc]
                        # GET TERMS IN DATA TRAIN
                        for term in doc_train[doc]['term']:
                            if term not in terms_train_fold:
                                terms_train_fold[term] = terms_train[term]
                
                # TRAIN-TEST NAIVE BAYES
                result,model = naive_bayes(doc_train_fold,doc_test_fold,terms_train_fold)
                evaluasi = confusion_matrix(doc_test_fold,result)

                # GET BEST MODEL
                if i == 1:
                    best = {'model':model, 'evaluasi':evaluasi}
                else:
                    if best['evaluasi']['f_measure']['avg'] < evaluasi['f_measure']['avg']:
                        best = {'model':model, 'evaluasi':evaluasi}
                
                # SAVE FOLD EVALUATION
                for j in evaluasi:
                    if j == 'akurasi':
                        fold[j]['fold-'+str(i)] = evaluasi[j]
                        fold[j]['avg'] += evaluasi[j]
                    else:
                        fold[j]['fold-'+str(i)] = evaluasi[j]['avg']
                        fold[j]['avg'] += evaluasi[j]['avg']

            for i in fold:
                fold[i]['avg'] = round(fold[i]['avg']/3, 3)

            model = best['model']['prob_term']
        
        print('\nHasil Evaluasi K-Fold Cross Validation :')
        for i in fold.items(): print(i)

        # SAVE MODEL
        Term_prob.objects.all().delete()
        for id,term in enumerate(model): 
            Term_prob.objects.create(
                id = id+1,
                term = term,
                anak = model[term]['anak'],            
                remaja = model[term]['remaja'],            
                dewasa = model[term]['dewasa'],            
            )
            
        # EVALUASI DATA TESTING (CEK OVERFITTING)
        result = testing_nb(doc_test,model)
        evaluasi_test = confusion_matrix(doc_test,result)
        print('\nHasil Evaluasi Data Testing :')
        for i in evaluasi_test: 
            if i == 'akurasi': print(i,'=',evaluasi_test[i])
            if i != 'akurasi': print(i,'=',evaluasi_test[i]['avg'])

        context ={
                'title' : 'Pengujian',
                'old' : request.POST,
                'evaluasi_train' : fold,
                'evaluasi_test' : evaluasi_test,
            }
        return render(request, 'ceritabali/pengujian.html', context)
    
    context ={
        'title' : 'Pengujian',
    }
    return render(request, 'ceritabali/pengujian.html', context)

def klasifikasi(request):
    if request.method == 'POST':
        # GET MODEL
        model = Term_prob.objects.filter().values()
        term_prob = {}
        for i in model:
            term_prob[i['term']] = {'anak':i['anak'],'remaja':i['remaja'],'dewasa':i['dewasa'],}
        
        # PREPROCESSING
        factory = StopWordRemoverFactory()
        stopword = factory.create_stop_word_remover()
        factory2 = StemmerFactory()
        stemmer = factory2.create_stemmer()
        doc = request.POST['judul'] + ' ' + request.POST['isi']
        # PREPROCESSING
        # -- case folding
        tokens = doc.lower()
        # -- remove angka
        tokens = re.sub(r"\d+", "", tokens)
        #remove punctuation
        tokens = tokens.translate(str.maketrans("","",string.punctuation))
        #remove whitespace leading & trailing
        tokens = tokens.strip()
        #remove multiple whitespace into single whitespace
        tokens = re.sub('\s+',' ',tokens)
        # -- tokenisasi
        tokens = word_tokenize(tokens)
        # -- normalization
        tokens = [i.replace('ã©', 'e').replace('ã¨', 'e').replace('ï¿½', 'e') for i in tokens]
        # -- filetering
        tokens = [stopword.remove(i) for i in tokens]
        # -- stemming
        tokens = [stemmer.stem(i) for i in tokens]

        # Klasifikasi
        # hitung probabilitas kelas
        hasil_test = {'anak':1,'remaja':1,'dewasa':1}
        for term in tokens:
            old_hasil_test = hasil_test.copy()
            if term in term_prob:
                hasil_test['anak'] *= term_prob[term]['anak']
                hasil_test['remaja'] *= term_prob[term]['remaja']
                hasil_test['dewasa'] *= term_prob[term]['dewasa']
            
            # lakukan normalisasi ketika decimal > e-324 (karena ketika decimal > e-324, decimal akan diubah menjadi 0.0) -- https://realpython.com/python-data-types/ --
            if hasil_test['anak'] == 0 or hasil_test['remaja'] == 0 or hasil_test['dewasa'] == 0:
                if max(old_hasil_test.values()) - min(old_hasil_test.values()) == 0:
                    for i in old_hasil_test: 
                        hasil_test[i] = 1
                else:
                    for i in old_hasil_test:
                        hasil_test[i] = (old_hasil_test[i] - min(old_hasil_test.values())) / (max(old_hasil_test.values()) - min(old_hasil_test.values())) + 0.001
                
        hasil_test['anak'] *= 1/3
        hasil_test['remaja'] *= 1/3
        hasil_test['dewasa'] *= 1/3

        # penentuan hasil naive bayes
        kelas = max(hasil_test, key=hasil_test.get)
        if kelas == 'anak': color = 'success'
        if kelas == 'remaja': color = 'warning'
        if kelas == 'dewasa': color = 'info'

        context ={
            'title' : 'Klasifikasi',
            'old' : request.POST,
            'kelas' : kelas,
            'color' : color,
        }
        return render(request, 'ceritabali/klasifikasi.html', context)

    context ={
        'title' : 'Klasifikasi',
    }
    return render(request, 'ceritabali/klasifikasi.html', context)

def refresh(request):
    if request.method == 'POST':
        preprocessing()
    return render(request, 'ceritabali/refresh.html')
