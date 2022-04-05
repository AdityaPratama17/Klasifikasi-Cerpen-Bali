from django.shortcuts import render, redirect
from .models import Document, Term, TF
from .komputasi.preprocessing import preprocessing, get_data
from .komputasi.naive_bayes import naive_bayes, test as testing_nb
from .komputasi.evaluasi import confusion_matrix
from .komputasi.genetic_algorithm import genetic_algorithm, evaluasi as eval_kfcv


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
            model,evaluasi = genetic_algorithm(doc_train,terms_train,generasi,jum_kromosom,len(terms_train),pc,pm)
        
        # TANPA SELEKSI FITUR
        else:
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
            model = best['model']
            evaluasi = best['evaluasi']
        
        print('\nHasil Evaluasi K-Fold Cross Validation :')
        for i in evaluasi: 
            if i == 'akurasi': print(i,'=',evaluasi[i])
            if i != 'akurasi': print(i,'=',evaluasi[i]['avg'])
            
        # EVALUASI DATA TESTING (CEK OVERFITTING)
        result = testing_nb(doc_test,terms,model['jum_term_kelas'],model['prob_term'])
        evaluasi_test = confusion_matrix(doc_test,result)
        print('\nHasil Evaluasi Data Testing :')
        for i in evaluasi_test: 
            if i == 'akurasi': print(i,'=',evaluasi_test[i])
            if i != 'akurasi': print(i,'=',evaluasi_test[i]['avg'])

        context ={
                'title' : 'Pengujian',
                'old' : request.POST,
                'evaluasi_train' : evaluasi,
                'evaluasi_test' : evaluasi_test,
            }
        return render(request, 'ceritabali/pengujian.html', context)
    
    context ={
        'title' : 'Pengujian',
    }
    return render(request, 'ceritabali/pengujian.html', context)

def klasifikasi(request):
    if request.method == 'POST':

        result = {'kelas':'ANAK', 'color':'info'}

        context ={
            'title' : 'Klasifikasi',
            'old' : request.POST,
            'result' : result,
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
