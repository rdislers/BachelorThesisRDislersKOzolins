import pickle
from sklearn import metrics
import os
import json
from data_process.sentence_normalizer import normalize_sentence
import xlsxwriter



def load_instances(clf_type):
    clf = pickle.load(open(f'{clf_type}_instances/{clf_type}_clf.pkl', 'rb'))
    count_vect = pickle.load(open(f'{clf_type}_instances/{clf_type}_count_v.pkl', 'rb'))
    tfidf_transformer = pickle.load(open(f'{clf_type}_instances/{clf_type}_tfidf_t.pkl', 'rb'))
    return clf, count_vect, tfidf_transformer


def test_classifier(clf, test_predict):
    y_test = pickle.load(open('data_process/data_sets/y_test.pkl', 'rb'))
    positions_categories = pickle.load(open('data_process/data_sets/positions_categories.pkl', 'rb'))
    print(metrics.classification_report(y_test, test_predict, target_names=positions_categories.categories))


def test_with_examples(clf_type, clf, count_vect, tfidf_transformer, lines):
    dict={}
    positions_categories = pickle.load(open('data_process/data_sets/positions_categories.pkl', 'rb'))
    # Classify new examples
    #with open('test_data/example_titles.csv',encoding='utf-8') as f:
    #lines = f.readlines()
    lines_without_n = [line.strip() for line in lines] #line.split('\n')[0]
    normalized_s = [normalize_sentence(l1) for l1 in lines_without_n]

    X_counts = count_vect.transform(normalized_s)
    X_tfidf = tfidf_transformer.transform(X_counts)
    y_result = clf.predict(X_tfidf)

    #with open(f'test_data/{clf_type}_results.tsv', 'w',encoding='utf-8') as file:
    for job_pos, classified_job in zip(lines_without_n, y_result):
        dict[job_pos]=positions_categories.categories[classified_job]
        #file.write(job_pos)
        #file.write("\t")
        #file.write(positions_categories.categories[classified_job])
        #file.write("\n")
    #file.close()
    return(dict)



#Build list of job titles
lines=[]
for filename in os.listdir('C:/Users/hokej/Desktop/LinkedinClassification/RAWSkills'):
    filenamefull='C:/Users/hokej/Desktop/LinkedinClassification/RAWSkills/'+filename
    with open(filenamefull,encoding="utf8") as f:
        content = json.load(f)
        lines.append(content["Title"].strip())


clf, count_vect, tfidf_transformer = load_instances('sgd')
X_test = pickle.load(open('data_process/data_sets/x_test.pkl', 'rb'))

# Test and show results
X_test_counts = count_vect.transform(X_test)
X_test_tfidf = tfidf_transformer.transform(X_test_counts)
test_predict = clf.predict(X_test_tfidf)
test_classifier(clf, test_predict)
dict=test_with_examples('sgd', clf, count_vect, tfidf_transformer,lines)


for filename in os.listdir('C:/Users/hokej/Desktop/LinkedinClassification/RAWSkills'):
    filenamefull='C:/Users/hokej/Desktop/LinkedinClassification/RAWSkills/'+filename
    with open(filenamefull,encoding="utf8") as f:
        content = json.load(f)
        title=content["Title"].strip()
        Department=dict.get(title, "No Match")
        content["Department"]=Department
        jsonname='C:/Users/hokej/Desktop/LinkedinClassification/ClassifiedComplete/'+filename
        with open(jsonname, 'w',encoding='utf-8') as file:
            json.dump(content,file)
