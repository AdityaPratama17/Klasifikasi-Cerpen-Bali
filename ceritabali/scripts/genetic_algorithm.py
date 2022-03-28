from .naive_bayes import naive_bayes
from .evaluasi import confusion_matrix
import numpy as np, random

def genetic_algorithm(doc_train,doc_test,terms_full,generasi,jum_kromosom,jum_gen,pc,pm):
    # INIT POPULATION
    kromosom,terms = init_population(terms_full,jum_kromosom,jum_gen)
    # EVALUATE
    total_fitness = 0
    for kr in kromosom:
        kr['fitness'],kr['model'],kr['evaluasi'] = evaluasi(doc_train,doc_test,terms_full,terms,kr['fitur'])
        total_fitness += kr['fitness']

    # ITERATE BY GENERASI
    for i in range(generasi):
        # SELECTION
        kromosom = selection(kromosom,jum_kromosom,total_fitness)
        # CROSSOVER
        offspring = crossover(kromosom,jum_kromosom,jum_gen,pc)
        # MUTATION
        offspring = mutation(kromosom,jum_gen,pm,offspring)
        # GET NEW POPULATION
        # -- evaluasi offspring
        for i in offspring:
            if sum(i) != jum_gen and sum(i) != 0:
                fitness,model,eval = evaluasi(doc_train,doc_test,terms_full,terms,i)
                kromosom.append({'fitur':i, 'fitness':fitness, 'model':model, 'evaluasi':eval})
        # -- sort & get new population
        for n in range(len(kromosom)-1, 0, -1):
            for i in range(n):
                if kromosom[i]['fitness'] < kromosom[i + 1]['fitness']:
                    kromosom[i], kromosom[i + 1] = kromosom[i + 1], kromosom[i]

        kromosom = kromosom[:jum_kromosom]
        # print('\n')
        # for i in kromosom: print(i['fitness'])
        # print(kromosom[0]['fitness'],sum(kromosom[0]['fitur']))        
    
    # GET BEST KROMOSOM 
    for i,kr in enumerate(kromosom):
        if  i == 0:
            best = kr
        else:
            if kr['fitness'] > best['fitness']: 
                best = kr
            elif kr['fitness'] == best['fitness'] and sum(kr['fitur']) < sum(best['fitur']):
                best = kr
    
    return kr['model'],kr['evaluasi']

def init_population(terms_full,jum_kromosom,jum_gen):
    kromosom = []
    for i in range(jum_kromosom):
        kromosom.append({
            'fitur':list(np.random.randint(low=2,size=jum_gen)),
            'fitness':0,
            'fold':{},
            'avg':{},
        })
    
    terms = []
    for term in terms_full:
        terms.append(term)
    
    return kromosom,terms

def evaluasi(doc_train,doc_test,terms,terms_only,fiturs):
    # SELECT TERM BY SELEKSI
    new_terms = {}
    for i,fitur in enumerate(fiturs):
        if fitur == 1:
            new_terms[terms_only[i]] = terms[terms_only[i]]
    
    # TRAIN & TEST
    result,model = naive_bayes(doc_train,doc_test,new_terms)
    evaluasi = confusion_matrix(doc_test,result)

    fitness = 0
    for i in evaluasi['f_measure']:
        fitness += evaluasi['f_measure'][i]
    fitness = round(fitness/3,5)

    return fitness,model,evaluasi

def evaluasi_bc(docs,terms,terms_only,fiturs):
    # SELECT TERM BY SELEKSI
    seleksi = []
    for i,fitur in enumerate(fiturs):
        if fitur == 1:
            seleksi.append(terms_only[i])

    fold = {}
    avg = {
        'akurasi' : 0,
        'precision' : {'anak':0,'remaja':0,'dewasa':0},
        'recall' : {'anak':0,'remaja':0,'dewasa':0},
        'f_measure' : {'anak':0,'remaja':0,'dewasa':0},
    }
    for i in range(1,4):
        # GET DATA TRAIN & TEST
        doc_train = {}
        doc_test = {}
        terms_train = {}
        for doc in docs:
            if docs[doc]['fold'] == i:
                doc_test[doc] = docs[doc]
            else:
                doc_train[doc] = docs[doc]
                # GET TERMS IN DATA TRAIN
                for term in docs[doc]['term']:
                    if term not in terms_train and term in seleksi:
                        terms_train[term] = terms[term]
        
        # TRAIN & TEST
        result = naive_bayes(doc_train,doc_test,terms_train,seleksi)
        evaluasi = confusion_matrix(doc_test,result)

        fold[i] = evaluasi
        for j in avg:
            if j == 'akurasi':
                avg[j] += evaluasi[j]
            else:
                for kelas in avg[j]:
                    avg[j][kelas] += evaluasi[j][kelas] 
        
    for j in avg:
        if j == 'akurasi':
            avg[j] = round((avg[j]/3),3)
        else:
            for kelas in avg[j]:
                avg[j][kelas] = round((avg[j][kelas]/3),3) 
    
    return fold,avg,avg['akurasi']

def selection(kromosom,jum_kromosom,total_fitness):
    # -- fitness relatif & komulatif
    qk = []
    for i,km in enumerate(kromosom):
        if i == 0:
            qk.append(km['fitness']/total_fitness)
        else:
            qk.append((km['fitness']/total_fitness)+qk[i-1])

    # -- seleksi
    new_kromosom = []
    rand = list(np.random.uniform(low=0.0, high=1.0, size=(jum_kromosom,)))
    for i,r in enumerate(rand):
        for j,value in enumerate(qk):
            if j == 0:
                if r <= value:
                    new_kromosom.append(kromosom[j])
                    break
            else:
                if r > qk[j-1] and r <= value:
                    new_kromosom.append(kromosom[j])
                    break
    
    return new_kromosom

def crossover(kromosom,jum_kromosom,jum_gen,pc):
    offspring = []
    # -- ambil induks
    induks = []
    while(len(induks)<2):
        induks = []
        rand = list(np.random.uniform(low=0.0, high=1.0, size=(jum_kromosom,)))
        for i,value in enumerate(rand):
            if value <= pc:
                induks.append(kromosom[i])
    # -- hapus 1 induk jika ganjil
    if len(induks)%2 == 1:
        induks = induks[:-1]
    # -- lakukan crossover
    for i,induk in enumerate(induks):
        if i % 2 == 0:
            cut = random.randint(1, jum_gen-1)
            offspring.append(induk['fitur'][:cut] + induks[i+1]['fitur'][cut:])
            offspring.append(induks[i+1]['fitur'][:cut] + induk['fitur'][cut:])

    return offspring

def mutation(kromosom,jum_gen,pm,offspring):
    new_offspring = offspring
    for kr in kromosom:
        temp = kr['fitur']
        rand = list(np.random.uniform(low=0.0, high=1.0, size=(jum_gen,)))
        edit = False
        for i,value in enumerate(rand):
            if value <= pm:
                if temp[i] == 1: temp[i] = 0
                else: temp[i] = 1
                edit = True
        if edit == True:
            new_offspring.append(temp)

    return new_offspring
