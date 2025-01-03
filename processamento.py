import os
import re


def processamento(doc):
  texto_completo = re.sub(r'\n+', '\n', doc)
  texto_completo = re.sub(r'./','', texto_completo)
  texto_completo = re.sub(r'/sic/', '', texto_completo)
  texto_completo = re.sub(r'/\?/', '?', texto_completo)
  texto_completo = re.sub(r'[|]', '', texto_completo)
  texto_completo = re.sub(r'\[|\]', '', texto_completo)
  texto_completo = re.sub(r'[/$]{1,2}','', texto_completo)
  texto_completo = re.sub(r'(?m)^.*\bC[oó]d\..*\n?', '', texto_completo)
  texto_completo = re.sub(r"\", "-", texto_completo)
  texto_completo = re.sub(r'  +', ' ', texto_completo)
  return texto_completo


path = "textos"
path2 = "textos_processados"
for name_doc in os.listdir(path):
  print(name_doc)
  with open(os.path.join(path, name_doc),'r',encoding='utf-8') as doc:
    texto = doc.read()
  
  texto_processado = processamento(texto)
  
  new_name = 'new_' + name_doc

  with open(os.path.join(path2, new_name),'w', encoding='utf-8') as new_doc:
    new_doc.write(texto_processado)
