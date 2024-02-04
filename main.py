import re

def abrir_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            contenido = archivo.read()
        return contenido
    except Exception as e:
        print(f"Ocurrió un error al intentar abrir el archivo: {e}")
        return None

def tokenizador(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            contenido = archivo.read()


            contenido = re.sub(r'(can-put\?|can-pick\?|can-move\?|move-dir|move-face|run-dirs)', r'\1', contenido)

       
            tokens = re.findall(r'\b\w+\b|\S+(?:-\S+)*|\S+\?', contenido)
            
            return tokens
    except Exception as e:
        print(f"Ocurrió un error al intentar abrir el archivo: {e}")
        return None

nombre_archivo = 'prueba.txt'
tokens = tokenizador(nombre_archivo)
if tokens:
    print(tokens)
else:
    print("Hubo problemas al tokenizar el archivo")
