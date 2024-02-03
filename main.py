import re

def abrir_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            contenido = archivo.read()
        return contenido
    except:
        print(f"Ocurrió un error al intentar abrir el archvo: {e}")
        return None

def tokenizador(nombreArchivo):
    try:
        with open(nombreArchivo, 'r') as archivo:
            contenido = archivo.read()
            tokens = re.findall(r'\S|\w', contenido)
            return tokens
    except:
        print(f"Ocurrió un error al intentar  abrir el archivo: {e}")
        return None

nombreArchivo = 'prueba.txt'
tokens = tokenizador(nombreArchivo)
if tokens:
    print(tokens)
else:
    print("Hubo problemas al tokenizar el archivo")
 