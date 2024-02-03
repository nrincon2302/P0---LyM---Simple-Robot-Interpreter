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
            tokens = re.findall(r'\b\w+\b|\S', contenido)
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
