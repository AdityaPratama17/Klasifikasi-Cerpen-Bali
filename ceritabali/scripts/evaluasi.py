def confusion_matrix(doc_test,result):
    # -- Confusion Matrix
    cm = {
        'anak' : {'anak':0,'remaja':0,'dewasa':0},
        'remaja' : {'anak':0,'remaja':0,'dewasa':0},
        'dewasa' : {'anak':0,'remaja':0,'dewasa':0},
    }
    for doc in doc_test:
        for aktual in cm:
            for prediktif in cm[aktual]:
                if doc_test[doc]['kelas'] == aktual and result[doc]['kelas'] == prediktif: 
                    cm[aktual][prediktif] += 1
    # for i in cm.items():print(i)
    # print('\n')

    # -- accuracy, precision & recall
    akurasi = 0
    precision = {}
    recall = {}
    f_measure = {}
    for aktual in cm:
        akurasi += cm[aktual][aktual]
        sum_p = 0
        sum_r = 0
        for prediktif in cm[aktual]:
            if prediktif != aktual:
                sum_p += cm[aktual][prediktif]
                sum_r += cm[prediktif][aktual]
        
        if cm[aktual][aktual] + sum_p != 0: 
            precision[aktual] = round((cm[aktual][aktual] / (cm[aktual][aktual] + sum_p))*100,3)
        else:
             precision[aktual] = 0
        if cm[aktual][aktual] + sum_r != 0: 
            recall[aktual] = round((cm[aktual][aktual] / (cm[aktual][aktual] + sum_r))*100,3)
        else: 
            recall[aktual] = 0
        if precision[aktual]+recall[aktual] != 0:
            f_measure[aktual] = round(2*((precision[aktual]*recall[aktual])/(precision[aktual]+recall[aktual])),3)
        else:
            f_measure[aktual] = 0
        
    akurasi = round((akurasi/len(doc_test))*100,3)

    return {'akurasi':akurasi,'precision':precision,'recall':recall,'f_measure':f_measure}


def confusion_matrix_bc(doc_test,result):
    # -- Confusion Matrix
    cm = {
        'anak' : {'anak':0,'remaja':0,'dewasa':0},
        'remaja' : {'anak':0,'remaja':0,'dewasa':0},
        'dewasa' : {'anak':0,'remaja':0,'dewasa':0},
    }
    for doc in doc_test:
        for aktual in cm:
            for prediktif in cm[aktual]:
                if doc_test[doc]['kelas'] == aktual and result[doc]['kelas'] == prediktif: 
                    cm[aktual][prediktif] += 1

    # -- accuracy, precision & recall
    akurasi = 0
    precision = [0,0,0]
    recall = [0,0,0]
    for i,aktual in enumerate(cm):
        akurasi += cm[aktual][aktual]
        sum_p = 0
        sum_r = 0
        for prediktif in cm[aktual]:
            if prediktif != aktual:
                sum_p += cm[aktual][prediktif]
                sum_r += cm[prediktif][aktual]
        
        if cm[aktual][aktual] == 0:
            if sum_p == 0 and sum_r == 0: 
                precision[i] = 1
                recall[i] = 1
            # if sum_p == 0: precision[i] = 1
            # if sum_r == 0: recall[i] = 1
        else:
            if cm[aktual][aktual] + sum_p != 0: precision[i] = cm[aktual][aktual] / (cm[aktual][aktual] + sum_p)
            if cm[aktual][aktual] + sum_r != 0: recall[i] = cm[aktual][aktual] / (cm[aktual][aktual] + sum_r)
        
        # print('precision[',aktual,'] :',precision[i])
        # print('recall[',aktual,'] :',recall[i])
    
    akurasi /= len(doc_test)
    precision = sum(precision)/len(cm)
    recall = sum(recall)/len(cm)
    # -- f-measure
    if precision+recall == 0: f_measure = 0
    else: f_measure = 2*((precision*recall)/(precision+recall))
    
    # for i in cm.items(): print(i)
    # print('akurasi :',akurasi)
    # print('precision :',precision)
    # print('recall :',recall)
    # print('f_measure :',f_measure)

    return [akurasi,precision,recall,f_measure]