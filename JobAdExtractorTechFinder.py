import requests
from bs4 import BeautifulSoup
import urllib.request
import time
from PIL import Image
import pytesseract
import json
import pandas as pd
import re
import fuzzywuzzy
import json
import os
import progressbar



def IndClassification(keyword):
    switcher={
                "b-darba-birza-b":'Labor_Exchange',
                "b-prakse-b":'Internship',
                "administrativais-darbs-asistesana":'Assistant',
                "bankas-apdrosinasana":'Banks',
                "buvnieciba-nekustamais-ipasums":'Real_Estate',
                "cilvēkresursi":'HR',
                "drosiba-glabsanas-dienesti-aizsardziba":'Rescue',
                "elektronika-telekomunikacijas":'Electronics-Telecommunication',
                "energetika-elektroenergija":'Energetics',
                "farmacija":'Pharma',
                "finanses-grāmatvediba":'Finance',
                "informacijas-tehnologijas":'IT',
                "izglitiba-zinatne":'Education',
                "jurisprudence-tieslietas":'Law',
                "kultura-maksla-izklaide-sports":'Culture',
                "kvalitates-vadiba-kvalitates-kontrole":'Quality_Control',
                "lauksaimnieciba-vides-zinatne":'Agriculture',
                "medicina-sociala-aprupe":'Medicine',
                "mediji-sabiedriskas-attiecibas":'Media',
                "mezsaimnieciba-kokapstrade":'Forestry',
                "marketings-reklama":'Marketing',
                "pakalpojumi":'Services',
                "pardosana":'Sales',
                "razosana-rupnieciba":'Manufacturing',
                "sezonalais-darbs":'Seasonal',
                "tehniskas-zinatnes":'Technical',
                "tirdznieciba-iepirkumi-piegade":'Retail',
                "transports-loģistika":'Logistics',
                "turisms-viesnicas-edinasana":'Tourism',
                "vadiba":'Management',
                "valsts-parvalde":'Government'
             }
    return switcher.get(keyword,"Special")


def IndustryFinder(html_text):
    IndustryLst=[]
    soup=BeautifulSoup(html_text, 'html.parser')
    keyword_tag = soup.find(attrs={"name": "keywords"})
    keywrdlst = keyword_tag['content'].split(",")
    targetlst=["administrativais-darbs-asistesana","b-darba-birza-b","b-prakse-b","bankas-apdrosinasana","buvnieciba-nekustamais-ipasums","cilvēkresursi","drosiba-glabsanas-dienesti-aizsardziba","elektronika-telekomunikacijas","energetika-elektroenergija","farmacija","finanses-grāmatvediba","informacijas-tehnologijas","izglitiba-zinatne","jurisprudence-tieslietas","kultura-maksla-izklaide-sports","kvalitates-vadiba-kvalitates-kontrole","lauksaimnieciba-vides-zinatne","marketings-reklama","medicina-sociala-aprupe","mediji-sabiedriskas-attiecibas","mezsaimnieciba-kokapstrade","pakalpojumi","pardosana","razosana-rupnieciba","sezonalais-darbs","tehniskas-zinatnes","tirdznieciba-iepirkumi-piegade","transports-loģistika","turisms-viesnicas-edinasana","vadiba","valsts-parvalde"]

    for item in keywrdlst:
        if item in targetlst:
            IndustryLst.append(IndClassification(item))

    return IndustryLst

def FindJobPosts(webpage):
    page=requests.get(webpage)
    page_text=page.text
    soup = BeautifulSoup(page_text, 'html.parser')
    mydivs = soup.findAll("div", {"class": "offer_primary_info"})
    Ads=[]
    for div in mydivs:
        child=div.findChildren("h2")
        ref=child[0].findAll("a")
        URL=("https://"+(ref[0]['href'][2:]))
        Ads.append(URL)
    return Ads

def IsImageAD(html_text):
    soup2=BeautifulSoup(html_text, 'html.parser')
    imgtag=soup2.find(id="JobAdImage")
    if imgtag==None:
        return False
    else:
        return True

def SemiStructuredAD(html_text):
    soup=BeautifulSoup(html_text, 'html.parser')
    MainContent=soup.find(id="page-main-content")
    if MainContent==None:
        return False
    else:
        return True

def LanguageOfAd(URL):
    urlsplit=URL.split("/")
    URLdef=urlsplit[3]
    lang="LV"
    if URLdef=="darba-sludinajums":
        lang="LV"
    elif URLdef=="job-ad":
        lang="ENG"
    elif URLdef=="objavlenie-o-rabote":
        lang="RUS"
    return lang


def Extractor(URL):
    content={}
    urlsplit=URL.split("/")
    name=urlsplit[4]+"_"+urlsplit[5].split("?")[0]
    html=requests.get(URL)
    html_text=html.text
    ImgBool=IsImageAD(html_text)
    RegularAdBool = SemiStructuredAD(html_text)
    soup=BeautifulSoup(html_text, 'html.parser')
    lang=LanguageOfAd(URL)
    ###Title and Salary Extraction###
    if RegularAdBool:
        divs = soup.findAll("div", {"class": "application-title flex-item"})
        if not divs:
            content["Title"]="Unknown"
        else:
            child=divs[0].findChildren("h1")
            content["Title"]=child[0].text

        ul = soup.findAll("ul", {"class": "application-info"})
        if not ul:
            content["Salary"]="Unknown"
        else:
            li= ul[0].find_all("li")
            try:
                content["Salary"]=li[0].text.split(":")[1].strip()
            except:
                content["Salary"]=li[0].text

        content["Industry"]=IndustryFinder(html_text)
        print(content["Industry"])
    #################################
    ###Content Extraction###
        if ImgBool:
            imgHTMLname=lang+"/"+"ImgHTML/"+name
            with open(imgHTMLname, 'w',encoding='utf-8') as file:
                file.write(html_text)
            imgname=lang+"/"+"Images/"+name.split(".")[0]+".jpg"
            imglink=soup.find(id="JobAdImage")
            link="https://www.cv.lv"+imglink['src']
            urllib.request.urlretrieve(link, imgname)
            imgtext = pytesseract.image_to_string(Image.open(imgname))
            content["MainContent"]=imgtext

        else:
            RegHTMLname=lang+"/"+"HTML/"+name
            with open(RegHTMLname, 'w',encoding='utf-8') as file:
                file.write(html_text)
            MainContent=soup.find(id="page-main-content")
            content["MainContent"]=MainContent.get_text()


        jsonname=lang+"/"+"Json/"+name.split(".")[0]+".json"
        with open(jsonname, 'w',encoding='utf-8') as file:
            json.dump(content,file)

        txtname=lang+"/"+"TxtFiles/"+name.split(".")[0]+".txt"
        with open(txtname, 'w',encoding='utf-8') as file:
            file.write(content["Title"]+"\n")
            file.write(content["Salary"]+"\n")
            for i in content["Industry"]:
                file.write(i+" ")
            file.write("\n")
            file.write(content["MainContent"])


    else:
        with open("NotExtractedURL.txt", "a" ,encoding='utf-8') as text_file:
            text_file.write(URL+"\n")
        nameNotExt="NotExtractedHTML/"+name
        with open(nameNotExt, 'w',encoding='utf-8') as file:
            file.write(html_text)

def AccentureExt(URL):
    content={}
    urlsplit=URL.split("/")
    name=urlsplit[4]+"_"+urlsplit[5].split("?")[0]
    html=requests.get(URL)
    html_text=html.text
    soup=BeautifulSoup(html_text, 'html.parser')
    framelink=soup.find(id="JobAdFrame")
    if framelink==None:
        Extractor(URL)
    else:
        lst=framelink["src"].split("/")
        FrameURL="https://my.accenture.lv/"+lst[4]+"/"+lst[5]
        html=requests.get(FrameURL)
        html_text=html.text
        soup=BeautifulSoup(html_text, 'html.parser')
        content["Title"]=soup.findAll("h1", {"class": "one-word-per-line"})[0].text
        content["Salary"]="0";
        content["Industry"]=["IT"]
        content["MainContent"]=soup.get_text()

        jsonname="ENG"+"/"+"Json/"+name.split(".")[0]+".json"
        with open(jsonname, 'w',encoding='utf-8') as file:
            json.dump(content,file)

        RegHTMLname="ENG"+"/"+"HTML/"+name
        with open(RegHTMLname, 'w',encoding='utf-8') as file:
            file.write(html_text)

        txtname="ENG"+"/"+"TxtFiles/"+name.split(".")[0]+".txt"
        with open(txtname, 'w',encoding='utf-8') as file:
            file.write(content["Title"]+"\n")
            file.write(content["Salary"]+"\n")
            for i in content["Industry"]:
                file.write(i+" ")
            file.write("\n")
            file.write(content["MainContent"])


def main():
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    for i in range(0,29):
        #page='https://www.cv.lv/darba-sludinajumi/visi?page='+str(i)
        page="https://www.cv.lv/darba-sludinajumi/visi?page="+str(i)
        lst=FindJobPosts(page)
        print(i)
        for ad in lst:
            print(ad)
            adcompany=ad.split("/")[4]
            if adcompany=="accenture-latvijas-filiale":         ###ACENTURE EXTRACTION
                AccentureExt(ad)
            else:                                              ##Regular Extraction
                Extractor(ad)
            time.sleep(2)
    import pandas as pd
import re
import fuzzywuzzy
import json
import os
import progressbar




industries=["Labor_Exchange",
"Internship",
"Assistant",
"Banks",
"Real_Estate",
"HR",
"Rescue",
"Electronics-Telecommunication",
"Energetics",
"Pharma",
"Finance",
"IT",
"Education",
"Law",
"Culture",
"Quality_Control",
"Agriculture",
"Medicine",
"Media",
"Forestry",
"Marketing",
"Services",
"Sales",
"Manufacturing",
"Seasonal",
"Technical",
"Retail",
"Logistics",
"Tourism",
"Management",
"Government"]
IndSkill={}
for i in industries:
    IndSkill[i]={}

dataframe1 = pd.read_excel('Skill.xlsx',engine='openpyxl')
'''garbage=['job','on','working','competence',
'colleague','friends','skill','opportunity',
'cover','unica','forward','allen','ration',
'mentor','developer','experience','unity',
'education','integra','click','result','lease',
'requirements','integration','educational','worldwide',
'analysis','world','requirement','focus','language',
'payment','final','work','for','and','system','data',
'entry','software','the','systems','management','a','at',
'to','your','form','new','by','team','in','with',
'high','knowledge','international','strategic',
'of','payment','processing','services','web','documentation',
'technical','adobe', 'systems', 'the', 'accounting', 'database',
'reporting', 'software', 'enterprise', 'resource', 'planning',
'erp', 'language', 'human', 'information', 'system', 'management',
'solution', 'microsoft', 'dynamics', 'office', 'project', 'solutions',
'online', 'oracle', 'suite', 'server', 'sage', 'sap', 'web', 'scheduling',
'services', 'apache', 'apple', 'pro', 'autodesk', 'technologies', 'data',
'and', 'computer', 'control', 'technology', 'energy', 'google', 'resources',
'ibm', 'inventory', 'lexisnexis', 'visual', 'automation', 'for', 'windows',
'business', 'intelligence', 'point', 'of', 'siemens', 'manager', 'tax',
'analysis', 'engineering', 'tools', 'tracking', 'development', 'medical',
'advanced', 'application', 'billing', 'integrated', 'studio', 'network',
'modeling', 'virtual', 'processing', 'corporation', 'healthcare', '&',
'design', 'time', 'warehouse', 'financial', 'laboratory', 'group',
'automated', 'international', 'scientific', 'maintenance', 'supply',
'global', 'insight', '3d', 'graphics', 'support', 'associates',
'advantage', 'esri', 'document', 'digital', 'plus', 'electronic',
'records', 'learning', 'compliance', 'center', 'databases', 'image',
'professional', 'national', 'service', 'property', 'american', 'dental',
'emr', 'health', 'practice', 'research', 'clinical', 'patient', 'client',
'risk', 'assessment', 'thomson', 'safety', 'simulation', 'analyzer',
'monitoring', 'testing', 'imaging', 'code', 'library', 'calculator',
'elite', 'program', 'model', 'test', 'rockware','adobe', 'systems', 'tracker', 'atlassian', 'blackbaud', 'the', 'edge', 'construction', 'accounting', 'database',
'reporting', 'software', 'email', 'enterprise', 'resource', 'planning', 'exact', 'es', 'performance',
'extensible', 'markup', 'language', 'fund', 'graphic', 'presentation', 'halogen', 'human', 'information',
'system',  'capital', 'management', 'intuit', 'solution', 'microsoft',
'access', 'dynamics', 'frx',  'project', 'solutions', 'online', 'oracle',
'e-business', 'suite', 'peoplesoft', 'server', 'hypertext', 'relational', 'sage',
'web', 'browser', 'scheduling', 'amazon', 'services', 'apache', 'apple', 'final',
'cut', 'pro', 'technologies', 'data', 'modeler', 'calendar',
'and', 'cnc', 'computer', 'aided', 'manufacturing', 'customer', 'control', 'entry',
'technology', 'dynamic', 'energy', 'geographic',  'google', 'analytics',
'resources', 'ibm', 'cognos', 'notes', 'power', 'statistics', 'inventory', 'job',
'payroll',  'visual', 'easy', 'marketing', 'automation', 'exchange',
'internet', 'explorer', 'basic', 'for', 'applications', 'windows',  'business',
'intelligence', 'edition', 'financials',  'portfolio',
'personnel', 'point', 'of', 'sale', 'pos', 'tech', 'act!', 'mas',
'crystal', 'reports',  'siemens', 'nx', 'social', 'media', 'on', 'desktop',
'sales', 'manager', 'acquisition', 'tax',
'house', 'iwork', 'mac', 'pages', 'corel',
'mapping', 'ptc', 'editor', 'player', 'creative', 'avid', 'composer', 'analysis',
'contact', 'visualization', 'in',  'plan', 'structure', 'reader', 'engineering',
'case', 'tools', 'tracking', 'development', 'aec',  'generator',
'bentley', 'medical', 'coding',
'real', 'estate', 'advanced', 'application', 'programming', 'billing', 'common',
'oriented', 'embarcadero', 'file', 'transfer', 'protocol', 'hewlett', 'packard',
'integrated', 'environment', 'process', 'consultants', 'framework','frameworks', 'active',
'front', 'page', 'studio', 'mobile', 'network', 'navigator', 'objective',
'quality', 'extraction', 'progress', 'workshop', 'programs',
'unified', 'modeling', 'virtual', 'private', 'terminal', 'expert', 'by', 'automatic',
'processing', 'pc', 'premier', 'small', 'asset', 'accounts', 'corporation',
'estimator', 'credit', 'healthcare', "moody's", 'kmv', 'abb', 'it', '&', 'design',
'time', 'warehouse', 'shipping', 'employee', 'financial', 'rational',
'industrial', 'production', 'plant',  'electric', 'statistical',
'computing', 'core', 'laboratory', 'group', 'automated',
'education', 'pq', 'element', 'international', 'systat', 'scientific', 'computerized',
'maintenance', 'distributed',  'machine', 'interface', 'gas', 'order',
'supply', 'chain', 'materials',  'airline',
'global', 'distribution', 'road',  'insight', 'freight', 'fms',
'feature)', '3d', 'transportation', 'advisor', 'rail',
'optimization', 'graphics', 'decision', 'support', 'route',
'associates', 'spreadsheet', 'event', 'attendance', 'catalyst', 'advantage',
'voyager', 'requirements', 'logistics', 'central',
'soft', 'operations', 'compass', 'hr',  'director', 'atlas',
'staff', 'files', 'west',  'document',  'bill', 'department',
'toolkit', 'limited',  'essentials',  'digital', 'ultimate',
'organization', 'chart', 'pay', 'electronics', 'centre', 'plus', 'travel',
'vision', 'la', 'interactive', 'electronic', 'records', 'new', 'world',
'recruiting',  'standard', 'talent', 'benefits', 'total', 'training',
'workplace',  'rapid', 'learning', 'lms', 'compliance', 'center',
'force', 'epic', 'ez', 'trainer', 'partner',  'tool',
'communications', 'knowledge', 'platform', 'intelligent', 'conversion',
'studios', 'learn', 'multimedia', 'ii', 'builder', 'open', 'assistant',
'safari', 'video', 'networks', 'content', 'innovative', 'ag', 'farm', 'smart',
'custom', 'mapper', 'positioning', 'landmark', 'response', 'microsystems',
'care', 'agriculture', 'consulting', 'trimble', 'works', 'databases', 'schedule',
'estimating', 'drafting',  'daily', 'image', 'impact', 'contractor', 'site', 'cash',
'flow',  'square', 'one', 'professional',  'school', 'keeper',
'public',  'student', 'sis', 'banner', 'connect', 'work', 'lifecycle', 'product',
'dassault', 'systemes',  'drawing',  'object',
'national', 'instruments', 'mind', 'water', 'surface',  'food', 'express',
'restaurant', 'service', 'positive', 'reservation', 'recipe', 'menu', 'life',
'hotel', 'micros', 'property', 'allscripts', 'misys', 'american', 'association',
'cerner', 'contract', 'dental', 'record', 'health', 'centricity', 'henry',
'schein', 'practice', 'mckesson', 'horizon', 'meditech', 'nuance',
'research', 'clinical', 'drug', 'capture', 'collection', 'patient', 'profiles',
'sciences', 'spatial', 'analyst', 'wallingford', 'facility', 'postal', 'boundary',
'vehicle', 'activity', 'card', 'investment', 'residential', 'master', 'turtle',
'commercial', 'client', 'publishing', 'emergency', 'team', 'register',
'doublebridge', 'rosetta', 'ectd', 'viewer', 'technical',  'review',
'mediregs', 'monitor', 'pharmaceutical', 'risk', 'assessment', 'viewpoint', 'complete',
'regulatory', '360', 'environmental', 'safety',
'insurance', 'portal', 'report', 'designer', 'collaborative', 'execution',
'scale', 'simulation', 'incident', 'command', 'physical',
'loss', 'prevention', 'operating', 'diagnostic', 'area', 'programmable', 'logic',
'controller', 'plc', 'wide', 'retail', 'star', 'millennium', 'material', 'planner',
'simulator', 'cost', 'estimation', 'base', 'spectrum', 'incorporated', 'agency',
'direct', 'claims', 'dispatch', 'fraud',  'pathways', 'appraisal',
'administration', 'clear', 'voice', 'stress', 'analyzer', 'corporate',
'fault', 'fair', 'isaac', 'first', 'legal', 'detection', 'zone', 'architect',
'statement', 'mitchell', 'river', 'field', 'location', 'mass', 'monitoring',
'computer-assisted', 'testing', 'imaging', 'scanning', 'simulators', 'driver',
'measurement', 'traffic', 'eeo', 'simple', 'peopleclick', 'screening',
'identification',  'conest', 'build', 'matrix',
'bond', 'code', 'platinum', 'main', 'sequence', 'micro', 'my', 'resume',
'search', 'products', 'enterprises', 'iq', 'laborsoft', 'laborforce',
'module', 'failure', 'effects',  'reliability',
'integration', 'foundation', 'industry', 'toolbox', 'ems',
'directory', 'actuarial', 'generation', 'self-service', 'administrator',
'forecast', 'library', 'workstation', 'survey',  'adaptive',
'maker',  'market', 'package', 'link', 'architectural',
'building', 'roof', 'calculator', 'elite', 'audit', 'labs', 'home',
'program', 'model',  'threat', 'guidance', 'intrusion',
'live', 'photo', 'editing', 'secure', 'gateway', 'tivoli',
'interchange', 'optical', 'character', 'clarity',
'backup', 'strategic', 'retrieval',  'engine',
'writer', 'municipal', 'best', 'bna', 'forms', 'iv', 'general',
'account', 'lead', 'focus', 'integrator', 'summit', 'trade',
'universal', 'idea', 'recovery', 'pattern', 'index',
'a', 'mode', 'pocket', 'assisted', 'emerald', 'land', 'mars',
'terrain', 'everest', 'analytical', 'lending', 'experian',
'quest', 'aspen', 'dealmaven', 'company', 'imagine', 'trading', 'xl',
'economic', 'algorithm', 'finance', 'mathematical', 'to', 'montgomery',
'mentor', '@nalyst', 'recognition', 'workbench', 'calculation',
'u.s.',    'underwriting', 'auditing',
'transaction', 'state', 'rate', 'form', 'westlaw',  'loan', 'merlin',
'prime', 'debt', 'repair', 'aid', 'line', 'oms', 'north', 'creation', 'numerical',
'computational', 'mining', 'compilers', 'libraries', 'configuration',
'source', 'sun', '2', 'three-dimensional', 'architecture', 'description', 'component',
'remote', 'functional', 'with', 'circuit', 'developer',  'load',
'migration', 'personal', 'security', 'static', 'prediction', 'deployment', 'test',
'check', 'verification', 'user', 'root', 'kit', 'protection', 'compiler',
'symbolic', 'scheme', 'definition', 'inspector', 'm', 'archive', 'institute', 'embedded',
'path', 'storage', 'wind', 'bmc', 'catalog', 'log', 'capacity', 'golden', 'paradigm',
'documentation', 'routing', 'packet', 'discrete', 'gold', 'ticket', 'call', 'scanner',
'fluke', 'air', 'forge', 'sound',  'soil', 'panorama', 'continuous',
'city', 'pm', 'max', 'maya', 'expression', 'high', 'text',  'auto', 'lab',
'fast', 'or',  'science', 'applied', 'lt',
'reality', 'precision', 'vector', 'carlson', 'logging',  'microsurvey',
'geomatics', 'ansys', 'computer-aided', 'thermal', 'equipment', 'finite',
'solid',  'hardware', 'instrument', 'molecular',
'motion', 'schematic', 'evaluation',
'synthesis', 'semiconductor', 'magic', 'blast', 'synopsys', 'signal', 'very',
'compact',  'fire', 'inspection', 'occupational',
'smoke', 'egress', 'consolidated', 'transport', 'egs', 'robotic', 'noldus',
'logger', 'marine', 'alias', 'mechanical', 'gamma', 'speed', 'gemcom',
'schlumberger', 'dose', 'codes', 'ihs', 'quick', 'dolphin', 'photon',
'robotics', 'paint', 'shop', 'digitizing', 'landscape', 'b', 'perkinelmer','ir','esi','ar','par', 'ca',
'devices', 'alphacam', 'vero', 'labeling', 'nature', 'dna', 'animal','automation', 'workload'
'nutrition', 'conservation',  'gene', 'protein',
'accelrys', 'chemistry', 'at', 'genetics', 'innovations', 'bruker',
'lading', 'netlims', 'orchard', 'lis', 'university', 'forest', 'clark',
'comet', 'table', 'waters', 'reference',  'synergy', 'radar',
'lakes', 'view', 'unidata', 'chemoffice', 'chemsw', 'groundwater',
'seismic', 'valley', 'waterloo', 'hydrogeologic', 'argus', 'series',
'delivery',  'telephone', 'pulse', 'train', 'bellview',
'iep', 'anywhere', 'medicine',  'audio', 'collections',
'political',  'academic', 'crime', 'assisi',
'act', 'career', 'educational', 'appointment', 'court', 'speech', 'ct',
'law', 'prolaw', 'visionary',  'screen', 'synapse', 'ats', 'x',
'fashion', 'ordering', 'music', 'piano', 'ear', 'laboratories', 'guide',
'translator', 'simply',  'exercise',
'scheduler',  'psychiatric', 'surgery',
'anatomic', 'pathology', 'blood', 'bank', 'transfusion', 'scc', 'sunquest',
'fox', 'printing', 'therapy', 'rating', 'idexx', 'depression', 'hearing',
'lucia', 'cbord', 'enforcement', 'shelter', 'store', 'salon', 'spa', 'agent',
'your', 'sabre', 'showing', 'kewill', 'flight', 'woodlands', 'logbook', 'bid',
'pile', 'asr', 'striker', 'aircraft',   'bindery']'''

#Chotlist=[]
#hotlist=[]
#check={}

done=0

bar = progressbar.ProgressBar(maxval=len(os.listdir('.')), \
   widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
bar.start()
for filename in os.listdir('.'):
    if filename.endswith(".json"):
        with open(filename,encoding="utf8") as f:
            content = json.load(f)
            txt=content['MainContent'].lower()
            #content['Skills']=[]
            x="C"
            #for x in dataframe1['Skills']:
            y=x.lower()
            if len(y)<=3:
                restring=r'[:;\'\"\\/.,?!-_=+ ()\W]{}[:;\'\"\\/.,?!-_=+ ()\W]'.format(re.escape(y))
            else:
                restring=r'[\s\S\w\W\d\D]{}[\s\S\w\W\d\D]'.format(re.escape(y))
            p=re.compile(restring,re.UNICODE)
            if p.search(txt):
                jsonname = 'Review/'+filename
                with open(jsonname, 'w',encoding='utf-8') as file:
                    json.dump(content,file)
                ###Simple check without spelling errors
                #Incl=False [ :,.\/-;()]
                #y=x.lower()
                #if len(y)<=3:
                #    restring=r'[:;\'\"\\/.,?!-_=+ ()\W]{}[:;\'\"\\/.,?!-_=+ ()\W]'.format(re.escape(y))
                #else:
                #    restring=r'[\s\S\w\W\d\D]{}[\s\S\w\W\d\D]'.format(re.escape(y))
                #p=re.compile(restring,re.UNICODE)
                #if p.search(txt):
                    #Incl=True
                    #check[x]=check.get(x,0)+1
                    #content['Skills'].append(x)
                    #if x not in Chotlist:
                    #    Chotlist.append(x)
                #    for i in content['Industry']:
                #        IndSkill[i][x]=IndSkill[i].get(x,0)+1


                #ysplt=y.split()
                #for i in ysplt:
                #    if i in garbage:
                #        continue
                #    else:
                #        restring=r'[ :,.\/-;()]{}[ :,.\/-;()]'.format(re.escape(i))
                #        p=re.compile(restring)
                #        if p.search(txt):
                #            Incl=True


                #if Incl:
                #    if x not in hotlist:
                #        hotlist.append(x)


            #jsonname = 'New/'+filename
            #with open(jsonname, 'w',encoding='utf-8') as file:
            #    json.dump(content,file)


    done=done+1
    bar.update(done)



bar.finish()
print(IndSkill)
#print(Chotlist)
#print(hotlist)
#print(check)

if __name__ == '__main__':
    main()
