def naive_bayes(doc_train,doc_test,terms):
    # -- Training
    jum_term_kelas,prob_term = train(doc_train,terms)
    # -- Testing
    result = test(doc_test,terms,jum_term_kelas,prob_term)
    
    return result, {'jum_term_kelas':jum_term_kelas,'prob_term':prob_term}

def train(doc_train,terms):
    jum_term_kelas = {'anak':0,'remaja':0,'dewasa':0}
    prob_term = {}
    for term in terms:
        prob_term[term] = {'anak':0,'remaja':0,'dewasa':0}
        for doc in doc_train:
            if doc_train[doc]['id'] in terms[term]:
                if doc_train[doc]['kelas'] == 'anak':
                    jum_term_kelas['anak'] += terms[term][doc_train[doc]['id']]
                    prob_term[term]['anak'] += terms[term][doc_train[doc]['id']]
                elif doc_train[doc]['kelas'] == 'remaja':
                    jum_term_kelas['remaja'] += terms[term][doc_train[doc]['id']]
                    prob_term[term]['remaja'] += terms[term][doc_train[doc]['id']]
                elif doc_train[doc]['kelas'] == 'dewasa':
                    jum_term_kelas['dewasa'] += terms[term][doc_train[doc]['id']]
                    prob_term[term]['dewasa'] += terms[term][doc_train[doc]['id']]
    
    for term in prob_term:
        prob_term[term]['anak'] = (prob_term[term]['anak']+1)/(jum_term_kelas['anak']+len(terms))
        prob_term[term]['remaja'] = (prob_term[term]['remaja']+1)/(jum_term_kelas['remaja']+len(terms))
        prob_term[term]['dewasa'] = (prob_term[term]['dewasa']+1)/(jum_term_kelas['dewasa']+len(terms))

    return jum_term_kelas,prob_term

def test(doc_test,terms,jum_term_kelas,prob_term):
    result = {}
    for doc in doc_test:
        # hitung probabilitas kelas
        hasil_test = {'anak':1,'remaja':1,'dewasa':1}
        for term in doc_test[doc]['term']:
            old_hasil_test = hasil_test.copy()
            # if term not in prob_term:
            #     hasil_test['anak'] *= 1/(jum_term_kelas['anak']+len(terms))
            #     hasil_test['remaja'] *= 1/(jum_term_kelas['remaja']+len(terms))
            #     hasil_test['dewasa'] *= 1/(jum_term_kelas['dewasa']+len(terms))
            # else:
            #     hasil_test['anak'] *= prob_term[term]['anak']
            #     hasil_test['remaja'] *= prob_term[term]['remaja']
            #     hasil_test['dewasa'] *= prob_term[term]['dewasa']
            if term in prob_term:
                hasil_test['anak'] *= prob_term[term]['anak']
                hasil_test['remaja'] *= prob_term[term]['remaja']
                hasil_test['dewasa'] *= prob_term[term]['dewasa']
            
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
        result[doc_test[doc]['id']] = {'kelas':max(hasil_test, key=hasil_test.get),'prob':max(hasil_test.values())}

    return result