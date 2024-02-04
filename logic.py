# Crear listas con caracteres reservados y palabras especiales del lenguaje
caracteres_reservados = ["(",")",":","-"]
comandos = ["defvar", "=", "move", "skip", "turn", "face", "put", "pick", "move-dir", "run-dirs", "move-face", "null"]
constantes = ["Dim", "myXpos", "myYpos", "myChips", "myBalloons", "balloonsHere", "ChipsHere", "Spaces"]
control = ["if", "loop", "repeat", "facing", "blocked", "can-put", "can-pick", "can-move", "isZero", "not", "defun"]


def parse(lexer_result):
    # Crear funcion para iniciar a analizar la sintaxis y usar las funciones de acuerdo al token identificado
    
    #Se comprueba que la cantidad de signos ( y ) sea consistente
    
    contar_parentesis(lexer_result)
    
    tokens = lexer_result.copy()
    instrucciones = []
    correctamente = []
    parentesis_abiertos = 0
    # Iterar sobre los tokens mientras que haya alguno sin procesar
    while len(tokens) > 0:
        # Revisar si inicia un paréntesis porque cada instrucción viene rodeada de uno
        token_actual = tokens.pop(0)
        if token_actual == "(":
            # Inicializar una lista para los tokens de un fragmento lógico
            fragmento_logico = []
            fragmento_logico.append(token_actual)
            parentesis_abiertos += 1
            
            # Repetir la extracción de paréntesis de inicio hasta llegar a una palabra reservada
            while tokens[0] == "(":
                fragmento_logico.append(tokens.pop(0))
                parentesis_abiertos += 1
                
            # Obtener el cuerpo principal de la instrucción, el primero que no es (
            principal = tokens.pop(0)
            fragmento_logico.append(principal)
            
            # Recorrer la instrucción mientras que no se cierre del todo
            while parentesis_abiertos > 0:
                token = tokens.pop(0)
                # Ajustar el contador según los paréntesis que encuentre
                if token == "(":
                    parentesis_abiertos += 1
                if token == ")":
                    parentesis_abiertos -= 1
                fragmento_logico.append(token)
            
            # En este punto, ya se habrá cerrado todo. Si no, seguiría en el ciclo
            instrucciones.append(fragmento_logico)
            
            # Verificar si el cuerpo principal es un comando, una función o un bloque de control
            # Hacer el parseo correspondiente y agregar el resultado a la lista de verificación
            if principal in comandos:
                correctamente.append(parse_comando(fragmento_logico))
            elif principal in control:
                correctamente.append(parse_control(fragmento_logico))
            else:
                correctamente.append(parse_funciones(fragmento_logico))

    # Estará bien escrito si no hay Falsos en la lista
    bien_escrito = False not in correctamente
    return bien_escrito
    
def parse_comando(instruccion):
    # verificar los comando pasa moverse derecha, izquierda, etc
    return None

def parse_control(instruccion):
    # verificar los comandos de control
    return None

def parse_funciones(instruccion):
    # verificar las funciones
    return None

def contar_parentesis(tokens):
    parentesisIniciales = sum(1 for token in tokens if token == '(')
    parentesisFinales = sum(1 for token in tokens if token == ')')
    if parentesisIniciales != parentesisFinales:
        raise Exception("La cantidad de paréntesis abiertos y cerrados no coincide.")

