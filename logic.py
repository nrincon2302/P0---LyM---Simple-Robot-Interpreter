# Crear listas con caracteres reservados y palabras especiales del lenguaje
import copy


caracteres_reservados = ["(",")",":","-"]
comandos = ["defvar", "=", "move", "skip", "turn", "face", "put", "pick", "move-dir", "run-dirs", "move-face", "null"]
constantes = ["dim", "myxpos", "myypos", "mychips", "myballoons", "balloonshere", "chipshere", "spaces"]
control = ["if", "loop", "repeat", "defun"]
condition = ["facing?", "blocked?", "can-put?", "can-pick?", "can-move?", "iszero", "not"]

#Tabla de simbolos para guardar las variables creadas por el usuario
tabla_simbolos = {}

#Diccionario para guardar las funciones junto con la cantidad de parametros que tiene
funcionesNumParametros = {}

#Agrego las contantes a mi tabla de simbolos para verificarlas al tiempo con las variables del usuario
for constante in constantes:
    tabla_simbolos[constante] = None
    
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
            parametros=[]
            #if principal in comandos:
            #    correctamente.append(parse_comando(fragmento_logico, parametros))
            #elif principal in control:
            #    correctamente.append(parse_control(fragmento_logico))
            #else:
            #    correctamente.append(parse_funciones(fragmento_logico))

    # Estará bien escrito si no hay Falsos en la lista
    bien_escrito = False not in correctamente
    return instrucciones
    
def parse_comando(instruccion, parametros):
    # verificar los comando pasa moverse derecha, izquierda, etc

    #verificar el uso de null
    if instruccion[1] == "null" and len(instruccion)==3:
        return True
    
    # Verificar si es una instrucción "defvar"
    elif instruccion[1] == "defvar":
        # Verificar si la instrucción tiene el formato correcto
        if len(instruccion) == 5 and instruccion[2].isidentifier() and instruccion[3].isdigit() and instruccion[2] not in tabla_simbolos.keys() and instruccion[2] not in constantes:
            nombre_variable = instruccion[2]
            valor_inicial = int(instruccion[3])
            #agregar el nuevo valor a la tabla de simbolos
            tabla_simbolos[nombre_variable]=valor_inicial  
            return True
    
    #verificar el uso correcto de la reasignacion de valores
    elif instruccion[1] == "=":
        if len(instruccion) == 5  and instruccion[3].isdigit() and instruccion[2] in tabla_simbolos.keys():
            tabla_simbolos[instruccion[2]]=int(instruccion[3])
            return True
    
    #verificar el uso correcto de las direcciones
    elif instruccion[1] in ["move", "skip", "turn", "face"]:
            if len(instruccion) == 4 and (instruccion[2].isdigit() or instruccion[2] in tabla_simbolos.keys()) or instruccion[3] in parametros:
                return True
    #verificar el uso correcto del put y el pick
    elif instruccion[1] in ["put", "pick"]:
        if len(instruccion) == 5 and instruccion[2] in [":balloons", ":chips"]:
           if instruccion[3].isdigit() or instruccion[3]in tabla_simbolos.keys() or instruccion[3]in parametros:
                    return True
        
    #verificar el uso correcto del move, run, move
    elif instruccion[1] in ["move-dir", "run-dirs", "move-face"] and len(instruccion) != 4:

        if instruccion[1] == "move-dir":
            if instruccion[2].isdigit() and instruccion[3] in [":front", ":right", ":left", ":back"]:

                return True
        elif instruccion[1] == "run-dirs":
            if len(instruccion) >= 4 and instruccion[-1] == ')':
                # Extraemos solo las direcciones de la lista de instrucción, excluyendo los paréntesis
                direcciones = instruccion[2:-1]
                # Verificamos que todas las direcciones sean válidas
                if all(dir in [":front", ":right", ":left", ":back",":up", ":down"] for dir in direcciones):
                    return True
        
        elif instruccion[1] == "move-face":
            if instruccion[2].isdigit() and instruccion[3] in [":north", ":south", ":west", ":east"]:
                return True
    
    #En caso de que no cumpla ninguno de estos casos se lanza la excepcion
    raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada")
    return None

def parse_control(instruccion):
    # verificar los comandos de control

    # Si es una instrucción de definición de función, lo parsea como tal
    if instruccion[1] == "defun":
         parse_funciones(instruccion)
    # Si es una instrucción de condicional
    elif instruccion[1] == "if":
        # Si sigue la estructura, el siguiente es un paréntesis y parsea la condición
        if instruccion[2] == "(":
            # Calcula la longitud esperada del condicional si es correcto
            longitud_condicional = 0
            if instruccion[3] == "facing?":
                longitud_condicional = 4
            elif instruccion[3] == "blocked?":
                longitud_condicional = 3
            elif instruccion[3] == "can-put?":
                longitud_condicional = 5
            elif instruccion[3] == "can-pick?":
                longitud_condicional = 5
            elif instruccion[3] == "can-move?":
                longitud_condicional = 4
            elif instruccion[3] == "isZero?":
                longitud_condicional = 4
            # Parsea el condicional específicamente
            parse_condition(instruccion[2:2+longitud_condicional])
            # Después del condicional, debe venir un comando o un bloque de control
            b1 = ["("]
            i = 2 + longitud_condicional + 1
            contador_parentesis = 1
            while contador_parentesis != 0:
                b1.append(instruccion[i])
                if instruccion[i] == "(":
                    contador_parentesis += 1
                if instruccion[i] == ")":
                    contador_parentesis -= 1
                i += 1
            # Parsear el primer bloque que se ha separado
            if b1[1] in comandos:
                parse_comando(b1, [])
            elif b1[1] in control:
                parse_control(b1)
            # Parsear el segundo bloque que se ha separado
            b2 = [instruccion[j] for j in range(i,len(instruccion)-1)]
            if b2[1] in comandos:
                parse_comando(b2, [])
            elif b2[1] in control:
                parse_control(b2)
                
            return True
        
        # Si no arranca en paréntesis después del if, se detiene el programa. Está mal
        else:
            raise Exception("La instrucción es un condicional. Se esperaba una condición después del IF.")
            
    # Si es una instrucción de bucle loop
    elif instruccion[1] == "loop":
        # Si sigue la estructura, el siguiente es un paréntesis y parsea la condición
        if instruccion[2] == "(":
            # Calcula la longitud esperada del condicional si es correcto
            longitud_condicional = 0
            if instruccion[3] == "facing?":
                longitud_condicional = 4
            elif instruccion[3] == "blocked?":
                longitud_condicional = 3
            elif instruccion[3] == "can-put?":
                longitud_condicional = 5
            elif instruccion[3] == "can-pick?":
                longitud_condicional = 5
            elif instruccion[3] == "can-move?":
                longitud_condicional = 4
            elif instruccion[3] == "isZero?":
                longitud_condicional = 4
            # Parsea el condicional específicamente
            parse_condition(instruccion[2:2+longitud_condicional])
            # Después del condicional, debe venir un comando o un bloque de control
            i = 2 + longitud_condicional
            # Parsear el bloque que se ha separado
            b = [instruccion[j] for j in range(i,len(instruccion)-1)]
            if b[1] in comandos:
                parse_comando(b, [])
            elif b[1] in control:
                parse_control(b)
        
            return True
        # Si no arranca en paréntesis después del if, se detiene el programa. Está mal
        else:
            raise Exception("La instrucción es un bucle. Se esperaba una condición después del LOOP.")

    # Si es una instrucción de repetición Repeat
    elif instruccion[1] == "repeat":
        # Si sigue la estructura, el siguiente es un número entero
        if instruccion[2].isdigit():
            # Le sigue ya sea un comando o un bloque de control
            b = [instruccion[k] for k in range(3, len(instruccion)-1)]
            # Parsear el bloque que se ha separado
            if b[1] in comandos:
                parse_comando(b, [])
            elif b[1] in control:
                parse_control(b)
        
            return True
        # Si no le sigue un número está mal
        else:
            raise Exception("La instrucción es un repeat. Se esperaba un número entero después del REPEAT.")

    return None

def parse_funciones(instruccion):
    # verificar las funciones
    
    #verifica si la funcion no existe 
    if instruccion[2] not in funcionesNumParametros.keys() and instruccion[3]=="(":
        instruccion_copia = copy.deepcopy(instruccion[3:])
        parametros = []
        x=0
        #verificar la correcta estructura de la funcion
        parentesis_abiertos = 0
         # Iterar sobre los tokens mientras que haya alguno sin procesar
        centinela = True
        while len(instruccion_copia) > 0 and centinela==True:
            # Revisar si inicia un paréntesis porque cada instrucción viene rodeada de uno
            token_actual = instruccion_copia.pop(0)
            
            if token_actual == "(":
                # Inicializar una lista para los tokens de un fragmento lógico
                fragmento_logico = []
                fragmento_logico.append(token_actual)
                parentesis_abiertos += 1
                
                # Repetir la extracción de paréntesis de inicio hasta llegar a una palabra reservada
                while instruccion_copia[0] == "(":
                    fragmento_logico.append(instruccion_copia.pop(0))
                    parentesis_abiertos += 1
                    
                # Obtener el cuerpo principal de la instrucción, el primero que no es (
                principal = instruccion_copia.pop(0)
                fragmento_logico.append(principal)
                
                # Recorrer la instrucción mientras que no se cierre del todo
                while parentesis_abiertos > 0:
                    token = instruccion_copia.pop(0)
                    # Ajustar el contador según los paréntesis que encuentre
                    if token == "(":
                        parentesis_abiertos += 1
                    if token == ")":
                        parentesis_abiertos -= 1
                    fragmento_logico.append(token)
        
                # Hacer el parseo correspondiente y agregar el resultado a la lista de verificación
                x+=1
                if x==1:
                    if any(isinstance(item, str) for item in fragmento_logico[1:-1]):
                        for item in fragmento_logico[1:-1]:
                             parametros.append(item)
                elif x>1:
                    parse_comando(fragmento_logico, parametros)
            
        #Agregar la funcion a el diccionario
        funcionesNumParametros[instruccion[2]] = parametros
        
        #Hacer el caso donde la funcion ya existe
        return True
    
            
        
    return None

def parse_condition(instruccion):
    # verificar las condiciones que se usan en la estrucutra de control if
    
    if instruccion[1] == "facing?" and len(instruccion) == 4:
        if instruccion[2] == "north" or instruccion[2] == "south" or instruccion[2] == "east" or instruccion[2] == "west":
            return True
    
    elif instruccion[1] == "blocked?" and len(instruccion) == 3:
        return True
    
    elif instruccion[1] == "can-put?" and len(instruccion) == 5:
        if instruccion[2] in ["chips", "balloons"] and instruccion[3].isdigit():
            return True
    
    elif instruccion[1] == "can-pick?" and len(instruccion) == 5:
        if instruccion[2] in ["chips", "balloons"] and instruccion[3].isdigit():
            return True
    
    elif instruccion[1] == "can-move?" and len(instruccion) == 4:
        if instruccion[2] in [":north", ":south", ":east", ":west"]:
            return True
    
    elif instruccion[1] == "isZero?" and len(instruccion) == 4:
        if instruccion[2].isdigit():
            return True
    
    raise Exception("La instrucción " + ' '.join(instruccion) + " no tiene la forma esperada")
   
    return False


def contar_parentesis(tokens):
    parentesisIniciales = sum(1 for token in tokens if token == '(')
    parentesisFinales = sum(1 for token in tokens if token == ')')
    if parentesisIniciales != parentesisFinales:
        raise Exception("La cantidad de paréntesis abiertos y cerrados no coincide.")

