from logic import parse
import re

def app():
    print("\n*********************************************")
    print("*                                           *")
    print("*          Bienvenido al Analizador         *")
    print("*               Sintáctico                  *")
    print("*                                           *")
    print("*          Hecho por Carol Florido          *")
    print("*              y Nicolás Rincón             *")
    print("*                                           *")
    print("*********************************************\n")
    
    nombre_archivo="miniTest.txt"
    contenido = abrir_archivo(nombre_archivo)
    tokens = tokenizador(contenido)
    try:
        if parse(tokens, False):
            print("TRUE -> El programa se encuentra correctamente escrito.")
        else:
            print("FALSE -> El programa no se encuentra correctamente escrito.")
    except Exception as e:
     
        print("FALSE -> El programa no se encuentra correctamente escrito.")

#Funcion para abrir un archivo en formato txt
def abrir_archivo(nombre_archivo):
    try:
        with open(nombre_archivo, 'r') as archivo:
            contenido = archivo.read()
        return contenido
    except Exception as e:
        print(f"Ocurrió un error al intentar abrir el archivo: {e}")
        return None
    
#funcion para tokenizar el lenguaje del archivo
def tokenizador(contenido):
    # Convertir todo el contenido a minúsculas
    contenido = contenido.lower()
    
    # Tokenizar, incluyendo palabras específicas y paréntesis como tokens individuales
    tokens = re.findall(r'(=|can-put\?|can-pick\?|facing\?|can-move\?|iszero\?|blocked\?|move-dir|move-face|run-dirs|:\w+|\b\w+\b|[()])', contenido)
    return tokens

app()
