#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Guillermo López Velarde González
# Updates by Ricardo Jimenez

import json
import re
import sys
from pymongo import MongoClient
import json

reload(sys)
sys.setdefaultencoding('utf8')


#Constantes útiles
articulos_en = r"\b(el|la|los|las|lo|al|del)\b"
articulos = r"\b(el|la|los|las|un|uno|una|unos|unas|lo|al|del)\b"
verbo_estar = r"\b[Ee]st(oy|ás|á|amos|áis|án|aba|abas|aba|ábamos|abais|aban|uve|uviste|uvo|uvimos|uvisteis|uvieron|aré|arás|ará|aremos|aréis|arán|aría|arías|aríamos|arían|é|és|emos|éis|én|uviera|uvieras|uviéramos|uvierais|uvieran|uviese|uvieses|uviese|uviésemos|uvieseis|uviesen|uviere|uvieres|uviere|uviéremos|uviereis|uvieren)\b"
verbo_estar_perfecto = r"\b[hH](e|as|a|emos|abéis|an|abía|abías|abía|abíamos|abíais|abían|ube|ubiste|ubo|ubimos|ubisteis|ubieron|abré|abrás|abrá|abremos|abréis|abrán|abría|abrías|abríamos|abríais|abrían|aya|ayas|ayamos|ayáis|ayan|ubiera|ubieras|ubiéramos|ubierais|ubieran|ubiese|ubieses|ubiésemos|ubieseis|ubiesen|ubiere|ubieres|ubiéremos|ubiereis|ubieren) +estado\b"
verbo_andar = r"\band(o|as|a|amos|áis|an|aba|abas|aba|ábamos|abais|aban|uve|uviste|uvo|uvimos|uvisteis|uvieron|aré|arás|ará|aremos|aréis|arán|aría|arías|aríamos|arían|e|es|emos|éis|en|uviera|uvieras|uviéramos|uvierais|uvieran|uviese|uvieses|uviese|uviésemos|uvieseis|uviesen|uviere|uvieres|uviere|uviéremos|uviereis|uvieren)\b"
verbo_andar_perfecto = r"\b(he|has|ha|hemos|habéis|han|había|habías|había|habíamos|habíais|habían|hube|hubiste|hubo|hubimos|hubisteis|hubieron|habré|habrás|habrá|habremos|habréis|habrán|habría|habrías|habríamos|habríais|habrían|haya|hayas|hayamos|hayáis|hayan|hubiera|hubieras|hubiéramos|hubierais|hubieran|hubiese|hubieses|hubiésemos|hubieseis|hubiesen|hubiere|hubieres|hubiéremos|hubiereis|hubieren) +andado\b"
verbo_ir = r"\bv(oy|as|a|amos|ais|an|aya|ayas|ayamos|ayáis|ayan)|\b(i|í)(ba|bas|bamos|bais|ban|ré|rás|rá|remos|réis|rán|ría|rías|ríamos|ríais|rían)|\bfu(i|iste|e|imos|isteis|eron|era|eras|éramos|erais|eran|ese|eses|ésemos|eseis|esen|ere|eres|éremos|ereis|eren)\b"
verbo_ir_perfecto = r"\b(he|has|ha|hemos|habéis|han|había|habías|había|habíamos|habíais|habían|hube|hubiste|hubo|hubimos|hubisteis|hubieron|habré|habrás|habrá|habremos|habréis|habrán|habría|habrías|habríamos|habríais|habrían|haya|hayas|hayamos|hayáis|hayan|hubiera|hubieras|hubiéramos|hubierais|hubieran|hubiese|hubieses|hubiésemos|hubieseis|hubiesen|hubiere|hubieres|hubiéremos|hubiereis|hubieren) +ido\b"
verbo_viajar = r"\bviaj(o|as|a|amos|áis|an|aba|abas|aba|ábamos|abais|aban|é|aste|ó|amos|asteis|aron|aré|arás|ará|aremos|aréis|arán|aría|arías|aríamos|arían|e|es|emos|éis|en|ara|aras|áramos|arais|aran|ase|ases|ásemos|aseis|asen|are|ares|áremos|areis|aren)\b"
verbo_viajar_perfecto = r"\b(he|has|ha|hemos|habéis|han|había|habías|había|habíamos|habíais|habían|hube|hubiste|hubo|hubimos|hubisteis|hubieron|habré|habrás|habrá|habremos|habréis|habrán|habría|habrías|habríamos|habríais|habrían|haya|hayas|hayamos|hayáis|hayan|hubiera|hubieras|hubiéramos|hubierais|hubieran|hubiese|hubieses|hubiésemos|hubieseis|hubiesen|hubiere|hubieres|hubiéremos|hubiereis|hubieren) +viajado\b"
s_patrones_mayusculas = r"\b(([A-ZÁÉÍÓÚÑ]+[ \b]+)+|[A-ZÁÉÍÓÚÑ][^A-ZÁÉÍÓÚÑ\W][^\W\d]+[ \b]+(([^A-ZÁÉÍÓÚÑ\W\d]+[ \b]+){,2}[A-ZÁÉÍÓÚÑ][^A-ZÁÉÍÓÚÑ\W][^\W\d]+[ \b]+)+)"
#Son cosas que marcan lo siguiente en una dirección. Colonia, esquina, "y", número, etc.
complemento_calle = r"((C|c)ol(\.)?(onia)?)|((B|b)arrio)"
calle = r"((C|c)alz(\.)?(ada)?|(c|C)alle|(A|a)venida)"
calles_mayus_numeros = r"([A-ZÁÉÍÓÚÑ]+[a-záéíóúñ]*[ \b]?)*(((N|n)(o|O)\.?)?#?[0-9]+)?"
calles_mayus = r"([A-ZÁÉÍÓÚÑ]+[a-záéíóúñ]*[ \b]?)*"
separador_calles = r"(, )?(y[ \b]|esquina[ \b])(con )?"
complemento_calles_minus=r"([a-záéíóúñA-ZÁÉÍÓÚÑ]*[ \b]?)*"


def preprocess(text):
    return re.sub(u'[^a-zA-Z0-9ñÑÁáÉéÍíÓóÚú#@ ]','',text)

def preprocess2(line):
    line = line.replace('á','a')
    line = line.replace('é','e')
    line = line.replace('í','i')
    line = line.replace('ó','o')
    line = line.replace('ú','u')
    line = line.replace('Á','A')
    line = line.replace('É','E')
    line = line.replace('Í','I')
    line = line.replace('Ó','O')
    line = line.replace('Ú','U')
    line = line.replace('\n',' ')
    line = re.sub(u'[^a-zA-Z0-9ñÑ#@ ]','',line)
    return line



def proceso_en(s_texto):
    """
    Patrones para lugares encontrados con "en"
    En general no arroja buenos resultados
    """
    en_articulos = articulos_en+r"( +[^A-ZÁÉÍÓÚÑ\W]+ +)*?" #Se muestran dos patrones principalmente, uno comienza con artículos
    en_mayusculas = s_patrones_mayusculas
    expresion_en = re.compile(r"(?<=\b[Ee]n )+("+en_articulos+en_mayusculas+"|"+en_mayusculas+")")# esta expresión encuentra todo lo que comienza con en, y le sigue un artículo con alguna mayúscula en algún punto, o puras mayúsculas. A los artículos, se les quitan los "un" y derivados, no parecen dar ningún buen resultado
    s_texto_encontrado = re.search(expresion_en,s_texto)
    if s_texto_encontrado:
        s_texto_encontrado = s_texto_encontrado.group(0).strip()
        if len(s_texto_encontrado.split()) > 6 or len(s_texto_encontrado) < 4: return ""
        stop_list = ["Vivo Chat","Messenger", "Twitter", "Facebook", "Internet", "Instagram", "Google", "Skype", "Tumblr", "Pocket", "Telegram", "Pinterest", "Reddit", "Linkedin", "Youtube", "Síguenos", "Inicio","Español","la cual","el cual","el que","hd","HD","pdf","PDF","la televisión"]
        for stop in stop_list:
            if s_texto_encontrado.startswith(stop):
                return ""
        #print (s_texto_encontrado)
        return s_texto_encontrado
    else:
        return ""
def proceso_calle(s_texto):
    """
    Patrones para encontrar calles. Se requiere explícitamente la palabra "calle"
    """
    #Strings que comiencen con una calle en "calle",luego palabra(s) que empiecen en mayúscula seguido o no de números, luego puede ir un separador_calles, y de nuevo palabras con mayúscula seguido o no de números. Todo, hasta encontrar palabra en minúscula.
    expresion_calle = re.compile(r""+calle+r"[ \b]"+calles_mayus_numeros+r"[ \b]?("+separador_calles+r""+calles_mayus+r")*")
    s_texto_encontrado = re.search(expresion_calle,s_texto)
    if s_texto_encontrado:
        s_texto_encontrado = s_texto_encontrado.group(0).strip()
        if len(s_texto_encontrado.split()) > 6 or len(s_texto_encontrado) < 4: return ""
        #quitamos todos los indicadores de un complemento, para dejar sólo la calle
        #expresion_colonia = re.compile(complemento_calle)
        #s_texto_encontrado = expresion_colonia.sub("",s_texto_encontrado)
        s_texto_encontrado = filtro_calles(s_texto_encontrado)
#       print (s_texto_encontrado)
        return s_texto_encontrado
    else:
        return ""
def proceso_complemento_calle(s_texto):
    """
    Patrones para calles que tienen colonia, número, o un complemento.
    """
    #Todo lo que haya después del complemento de la calle.
    expresion_calle = re.compile(r"("+complemento_calle+r")[ \b]"+complemento_calles_minus+r"")
    s_texto_encontrado = re.search(expresion_calle,s_texto)
    if s_texto_encontrado:
        s_texto_encontrado = s_texto_encontrado.group(0).strip()
        if len(s_texto_encontrado.split()) > 6 or len(s_texto_encontrado) < 4: return ""
        #expresion_colonia = re.compile(complemento_calle)
        #s_texto_encontrado = expresion_colonia.sub("",s_texto_encontrado)
        stop_list = ["https","http"," #"]
        for stop in stop_list:
            s_texto_encontrado = s_texto_encontrado.replace(stop,"")
#       print (s_texto_encontrado)
        return s_texto_encontrado
    else:
        return ""
def proceso_entre(s_texto):
    """
    Patrones para lugares encontrados con "entre"
    """
    expresion_entre=re.compile(r"("+verbo_estar+"|"+verbo_estar_perfecto+")"+" +entre +[\w ]+")
def proceso_cercalejos(s_texto):
    """
    Patrones para lugares encontrados con "cerca/lejos"
    """
    expresion_cerca_lejos=re.compile(r"("+verbo_estar+"|"+verbo_estar_perfecto+")"+" +(cerca|lejos) +de +[\w ]+")

def filtro_calles(s_texto_encontrado):
    s_texto_encontrado = s_texto_encontrado.strip()
    lista = s_texto_encontrado.split(" ")
    #Si sólo hay un elemento en la lista
    if len(lista)<=1:
        return ""
    else:
        return s_texto_encontrado

#Abrir el archivo
#with open("sept19_26.json","r") as archivo:

client = MongoClient('mongodb://localhost/sismos_filtrados')
db = client.sismos_filtrados

file_data = open('ner.json','w+')
ner = {}
total = 0
#por cada tuit
for parsed_tweet in db.sismos.find({}):
    if not parsed_tweet['truncated']:
        s_texto = parsed_tweet['text']
    else:
        s_texto = parsed_tweet['extended_tweet']['full_text']

    s_texto_encontrado_calle = proceso_calle(preprocess2(s_texto))
    if s_texto_encontrado_calle:
        total = total + 1
        aux = {}
        aux['Tweet'] = s_texto
        aux['Calle'] = s_texto_encontrado_calle
        #print ("Tweet:")
        #print (s_texto)
        #print ("Calle: ")
        #print (s_texto_encontrado_calle)
        s_texto_encontrado_complemento_calle = proceso_complemento_calle(preprocess2(s_texto))
        if s_texto_encontrado_complemento_calle:
            #print ("Complemento: ")
            #print (s_texto_encontrado_complemento_calle)
            aux['Complemento'] = s_texto_encontrado_complemento_calle
            #print ("\n")
        else:
            aux['Complemento'] = ''
            #print("\n")
        ner['Tweet_'+str(total)] = aux

file_data.write(json.dumps(ner))


file_data.close()


#       print ("original:")
#       print (s_texto)
#       print ("entidad:")
#       print (texto_encontrado)
#       print ("\n")
