from django.shortcuts import render, redirect
from .models import Document, Term, TF
from .scripts.preprocessing import preprocessing, get_data
from .scripts.naive_bayes import naive_bayes
from .scripts.evaluasi import confusion_matrix
from .scripts.genetic_algorithm import genetic_algorithm, evaluasi as eval_kfcv


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
        for doc in docs:
            if docs[doc]['tipe'] == 'train':
                doc_train[doc] = docs[doc]
            else:
                doc_test[doc] = docs[doc]
        
        if request.POST['seleksi'] == 'yes':
            avg_total={}
            # SELEKSI FITUR
            generasi = int(request.POST['iterasi'])
            jum_kromosom = int(request.POST['kromosom'])
            jum_gen = len(terms)
            pc = float(request.POST['cr'])
            pm = float(request.POST['mr'])
            seleksi,kromosom = genetic_algorithm(doc_train,terms,generasi,jum_kromosom,jum_gen,pc,pm)
            avg_total['train'] = {}
            for i in kromosom['avg']:
                if i != 'akurasi':
                    jum = 0 
                    for j in kromosom['avg'][i]:
                        jum += kromosom['avg'][i][j]
                    avg_total['train'][i] = round(jum/3,3)
            print('jum terms:',len(terms),', jum seleksi:',len(seleksi))
            print('\nhasil seleksi fitur (data train)')
            for i in kromosom['avg'].items(): print(i)

            # KLASIFIKASI (NAIVE BAYES)
            # -- GET TERMS IN DATA TRAIN
            terms_train = {}
            for doc in doc_train:
                for term in doc_train[doc]['term']:
                    if term not in terms_train:
                        terms_train[term] = terms[term]
            # -- TRAIN & TEST NAIVE BAYES
            result = naive_bayes(doc_train,doc_test,terms_train,seleksi)
            evaluasi = confusion_matrix(doc_test,result)
            avg_total['test'] = {}
            for i in evaluasi:
                if i != 'akurasi':
                    jum = 0 
                    for j in evaluasi[i]:
                        jum += evaluasi[i][j]
                    avg_total['test'][i] = round(jum/3,3)
            print('\nhasil seleksi fitur + NB (data test)')
            for i in evaluasi.items(): print(i)

            context ={
                'title' : 'Pengujian',
                'old' : request.POST,
                'fold' : kromosom['fold'],
                'avg' : kromosom['avg'],
                'evaluasi' : evaluasi,
                'avg_total': avg_total,
            }
            return render(request, 'ceritabali/pengujian.html', context)

        else:
            avg_total = {}
            # EVALUASI NB DENGAN KFCV TANPA GA 
            seleksi = [1 for i in range(len(terms))]
            term_only = [i for i in terms]
            fold,avg,fitness = eval_kfcv(doc_train,terms,term_only,seleksi)
            avg_total['train'] = {}
            for i in avg:
                if i != 'akurasi':
                    jum = 0 
                    for j in avg[i]:
                        jum += avg[i][j]
                    avg_total['train'][i] = round(jum/3,3)
            print('\nhasil tanpa seleksi fitur + NB (data train)')
            for i in avg.items(): print(i)

            # -- TRAIN & TEST NAIVE BAYES
            seleksi = [i for i in terms]
            terms_train = {}
            for doc in doc_train:
                for term in doc_train[doc]['term']:
                    if term not in terms_train:
                        terms_train[term] = terms[term]
            result = naive_bayes(doc_train,doc_test,terms_train,seleksi)
            evaluasi = confusion_matrix(doc_test,result)
            avg_total['test'] = {}
            for i in evaluasi:
                if i != 'akurasi':
                    jum = 0 
                    for j in evaluasi[i]:
                        jum += evaluasi[i][j]
                    avg_total['test'][i] = round(jum/3,3)
            print('\nhasil tanpa seleksi fitur + NB (data test)')
            for i in evaluasi.items(): print(i)

            context ={
                'title' : 'Pengujian',
                'old' : request.POST,
                'fold' : fold,
                'avg' : avg,
                'evaluasi' : evaluasi,
                'avg_total': avg_total,
            }
            return render(request, 'ceritabali/pengujian.html', context)

    context ={
        'title' : 'Pengujian',
    }
    return render(request, 'ceritabali/pengujian.html', context)

def refresh(request):
    if request.method == 'POST':
        preprocessing()
    return render(request, 'ceritabali/refresh.html')
