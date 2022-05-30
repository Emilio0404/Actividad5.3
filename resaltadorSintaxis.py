""" Actividad 3.4
Materia:Implementación de métodos computacionales.
Grupo: 604
Fecha: 13 de mayo de 2022
Integrantes:
    José Emilio Alvear Cantú  | A01024944
    Jorge Del Barco Garza     | A01284234
    Patricio mendoza Pasapera | A00830337
"""


import os.path
import sys


PALABRAS_RESERVADAS = [
    "auto", "else", "long", "switch", "break", "enum", "register",
    "typedef", "case", "extern", "return", "union", "char", "float",
    "short", "unsigned", "const", "for", "signed", "void", "continue",
    "goto", "sizeof", "volatile", "default", "if", "static", "while",
    "do", "int", "struct", "double", "main"
]

SEPARADORES = [
    "{", "}", "(", ")", "[", "]", ",", ";"
]

OPERADORES = [
    '+', '*', '%', '=', '>', '<', '!', '&', '?', ':', '~', '^',
    '|', "&lt", "&gt", "&amp", '.'
]

CHAR_REQUIERE_FORMATO = {
    '&' : '&amp',
    '<' : '&lt',
    '>' : '&gt',
    '"' : '&quot',
    "'" : '&#39'
}


def resaltadorSintaxis(_archivo):
    """Es el main del codigo"""
    
    # Abrir archivo de entrada
    inputFileHandle = open(_archivo)

    # Abrir archivo de salida. Se limpia el archivo automaticamente
    outputFileHandle = open("index.html", 'w', encoding="utf-8")

    # Agregar escructura básica del inicio de un documento HTML
    escribirInicioArchivoHTML(outputFileHandle)

    # Leer cada línea. Resaltarla y escribirla en el archivo HTML
    codigoResaltado = resaltar(inputFileHandle)
    escribirCodigoResaltadoEnHTML(codigoResaltado, outputFileHandle)

    # Agregar estructura del final de un documento HTML
    escribirFinalArchivoHTML(outputFileHandle)

    inputFileHandle.close()
    outputFileHandle.close()


def resaltar(htmlFile):

    NUEVO_PARRAFO_HTML = "</p>\n\t\t<p>"
    ESPACIO_HTML = "&nbsp;"

    codigoResaltado = ["\t\t<p>"]
    unfinishedToken = []
    estado = "inicial"

    # Se lee el documento de texto hasta que se acaben los caracteres
    while True:
        char = htmlFile.read(1)
        if not char:
            # Se termina de leer el documento, se cierra el último párrafo
            tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
            codigoResaltado.append(tokenEnHTML + "</p>")
            break

        if char in CHAR_REQUIERE_FORMATO:
            char = CHAR_REQUIERE_FORMATO[char]

        if estado == "inicial":
            if char.isalpha():
                estado = "variable"
                unfinishedToken.append(char)
            elif char == '0':
                estado = "octal"
                unfinishedToken.append(char)
            elif char.isnumeric():
                estado = "entero"
                unfinishedToken.append(char)
            elif char == '.':
                estado = "real_sin_parte_entera"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                unfinishedToken.append(char)
            elif char == "&#39":
                estado = "literal_caracter"
                unfinishedToken.append(char)
            elif char == '&quot':
                estado = "string"
                unfinishedToken.append(char)
            elif char == '/':
                estado = "division"
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = 'operador'
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                codigoResaltado.append(ESPACIO_HTML + NUEVO_PARRAFO_HTML)
                unfinishedToken = []
            elif char == "#":
                estado = "include_define"
                unfinishedToken.append(char)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break

        
        elif estado == "include_define":
            if char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                codigoResaltado.append(ESPACIO_HTML + NUEVO_PARRAFO_HTML)
                unfinishedToken = []
            elif char.isalpha():
                unfinishedToken.append(char)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "variable":
            if char.isalpha() or isInteger(char) or char == "_":
                estado = "variable"
                unfinishedToken.append(char)
            else:
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []

                if char == '/':
                    estado = "division"
                    unfinishedToken.append(char)
                elif char == '-':
                    estado = "resta"
                    unfinishedToken.append(char)
                elif isSeparator(char):
                    estado = "separador"
                    unfinishedToken.append(char)
                elif char == '.':
                    estado = "operador"
                    unfinishedToken.append(char)
                elif isOperand(char):
                    estado = 'operador'
                    unfinishedToken.append(char)
                elif char == ' ':
                    estado = "inicial"
                    codigoResaltado.append(ESPACIO_HTML)
                elif char == '\n':
                    estado = "inicial"
                    codigoResaltado.append(NUEVO_PARRAFO_HTML)
                else:
                    codigoResaltado.append(manejarErrorSintaxis())
                    break

        
        elif estado == "entero":
            if isInteger(char):
                estado = "entero"
                unfinishedToken.append(char)
            elif char == 'e' or char == 'E':
                estado = "entero_con_exponente"
                unfinishedToken.append(char)
            elif char == 'u' or char == 'U':
                estado = "unsigned_int"
                unfinishedToken.append(char)
            elif char == 'l' or char == 'L':
                estado = "long_int"
                unfinishedToken.append(char)
            elif char == '.':
                estado = "real"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == "/":
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break

        
        # Si recibe una E, se asegura de que el siguiente caracter sea entero o -
        elif estado == "entero_con_exponente":
            if isInteger(char):
                unfinishedToken.append(char)
                estado = 'entero_con_exponente_aux1'
            elif char == '-' or char == '+':
                unfinishedToken.append(char)
                estado = 'entero_con_exponente_aux2'
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        # Es valido para salir de numero real despues de recibir E o E-
        elif estado == "entero_con_exponente_aux1":
            if isInteger(char):
                unfinishedToken.append(char)
            elif char == 'u' or char == 'U':
                estado = "unsigned_int"
                unfinishedToken.append(char)
            elif char == 'l' or char == 'L':
                estado = "long_int"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == '/':
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        # Se asegura que despues de recibir un E- o E+, se reciba un numero
        elif estado == 'entero_con_exponente_aux2':
            if isInteger(char):
                unfinishedToken.append(char)
                estado = 'entero_con_exponente_aux1'
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "unsigned_int":
            if char == 'l' or char == 'L':
                estado = "unsigned_long_int"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == "/":
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "unsigned_long_int":
            if char == 'l' or char == 'L':
                estado = "unsigned_long_long_int"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == "/":
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "unsigned_long_long_int" or estado == "long_unsigned_int":
            if char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == "/":
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "long_int":
            if char == 'l' or char == 'L':
                estado = "long_long_int"
                unfinishedToken.append(char)
            elif char == 'u' or char == 'U':
                estado = "long_unsigned_int"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == "/":
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "long_long_int":
            if char == 'u' or char == 'U':
                estado = "unsigned_long_long_int"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == "/":
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "octal":
            if char == 'x' or char == 'X':
                estado = "hexadecimal"
                unfinishedToken.append(char)
            elif isInteger(char):
                if int(char) < 8:
                    estado = "octal"
                    unfinishedToken.append(char)
                else:
                    estado = "puede_ser_real"
                    unfinishedToken.append(char)
            elif char == '.':
                estado = "real"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == '/':
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break
            

        elif estado == "hexadecimal":
            # Debe recibir un numero hexadecimal despues de la x
            if char in "0123456789ABCDEF":
                estado = "hexadecimal_final"
                unfinishedToken.append(char)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break
        

        elif estado == "hexadecimal_final":
            if char in "0123456789ABCDEF":
                estado = "hexadecimal_final"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == "/":
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "real_sin_parte_entera":
            # Si no tiene parte entera o decimal antes de una E, es error. Se asegura
            # que si tenga parte decimal antes de un exponente si no hay parte entera.
            if isInteger(char):
                estado = "real"
                unfinishedToken.append(char)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "puede_ser_real":
            # Un octal empieza con 0. Si se recibe un numero mayor a 7 en el octal,
            # ya no es octal pero puede ser aún real. Para que sea real debe recibir un
            # punto. Si no recibe el punto, es un octal inválido
            if isInteger(char):
                unfinishedToken.append(char)
            elif char == ".":
                estado = "real"
                unfinishedToken.append(char)
            else:
                codigoResaltado.append(char)
                break


        elif estado == "real":
            if isInteger(char):
                unfinishedToken.append(char)
                estado = "real"
            elif char == 'E' or char == 'e':
                estado = "real_aux1"
                unfinishedToken.append(char)
            elif char == 'f' or char == 'F':
                estado = "fin_real_con_f"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == '/':
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        # Si recibe una E, se asegura de que el siguiente caracter sea entero o -
        elif estado == "real_aux1":
            if isInteger(char):
                unfinishedToken.append(char)
                estado = 'real_aux2'
            elif char == '-' or char == '+':
                unfinishedToken.append(char)
                estado = 'real_aux3'
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        # Es valido para salir de numero real despues de recibir E o E-
        elif estado == "real_aux2":
            if isInteger(char):
                unfinishedToken.append(char)
                estado = "real_aux2"
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == '/':
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        # Se asegura que despues de recibir un E- o E+, se reciba un numero
        elif estado == 'real_aux3':
            if isInteger(char):
                unfinishedToken.append(char)
                estado = 'real_aux2'
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "fin_real_con_f":
            if isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == '/':
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "resta":
            if char.isalpha():
                estado = "variable"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == '0':
                estado = "octal"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char.isnumeric():
                estado = "entero"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ".":
                estado = "real"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == '/':
                estado = "division"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == '&quot':
                estado = "string"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == "&#39":
                estado = "literal_caracter"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = "operador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "division":
            if char == '/':
                estado = "comentario"
                unfinishedToken.append(char)
            elif char == '*':
                estado = "comentario_multilinea"
                unfinishedToken.append(char)
            else:
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []

                if char.isalpha():
                    estado = "variable"
                    unfinishedToken.append(char)
                elif char == '0':
                    estado = "octal"
                    unfinishedToken.append(char)
                elif char.isnumeric():
                    estado = "entero"
                    unfinishedToken.append(char)
                elif char == '.':
                    estado = "real"
                    unfinishedToken.append(char)
                elif char == '-':
                    estado = "resta"
                    unfinishedToken.append(char)
                elif char == "&#39":
                    estado = "caracter"
                    unfinishedToken.append(char)
                elif char == '&quot':
                    estado = "string"
                    unfinishedToken.append(char)
                elif char == '/':
                    estado = "division"
                    unfinishedToken.append(char)
                elif isOperand(char):
                    estado = 'operador'
                    unfinishedToken.append(char)
                elif char == ' ':
                    estado = "inicial"
                    tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                    codigoResaltado.append(tokenEnHTML)
                    unfinishedToken = []
                    codigoResaltado.append(ESPACIO_HTML)
                elif char == '\n':
                    estado = "inicial"
                    tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                    codigoResaltado.append(tokenEnHTML)
                    codigoResaltado.append(NUEVO_PARRAFO_HTML)
                    unfinishedToken = []
                else:
                    codigoResaltado.append(manejarErrorSintaxis())
                    break
                

        elif estado == "operador":
            tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
            codigoResaltado.append(tokenEnHTML)
            unfinishedToken = []

            if char.isalpha():
                estado = "variable"
                unfinishedToken.append(char)
            elif char == '0':
                estado = "octal"
                unfinishedToken.append(char)
            elif char.isnumeric():
                estado = "entero"
                unfinishedToken.append(char)
            elif char == '.':
                estado = "real"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                unfinishedToken.append(char)
            elif char == "&#39":
                estado = "caracter"
                unfinishedToken.append(char)
            elif char == '&quot':
                estado = "string"
                unfinishedToken.append(char)
            elif char == '/':
                estado = "division"
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = 'operador'
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
                unfinishedToken = []
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "comentario":
            if char == '\n':
                estado = "inicial"
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
                unfinishedToken = []
            else:
                if char == ' ':
                    unfinishedToken.append(ESPACIO_HTML)
                else:
                    unfinishedToken.append(char)

        
        elif estado == "comentario_multilinea":
            if char == '*':
                estado = "cerrar_comentario_multilinea"
                unfinishedToken.append(char)
            elif char == '\n':
                token = ''.join(unfinishedToken)
                codigoResaltado.append(f'<span class="comentario">{token}</span>')
                codigoResaltado.append(ESPACIO_HTML + NUEVO_PARRAFO_HTML)
                unfinishedToken = []
            elif char == ' ':
                unfinishedToken.append(ESPACIO_HTML)
            else:
                unfinishedToken.append(char)

        
        elif estado == "cerrar_comentario_multilinea":
            if char == "/":
                estado = "inicial"
                unfinishedToken.append(char)
                token = ''.join(unfinishedToken)
                codigoResaltado.append(f'<span class="comentario">{token}</span>')
                unfinishedToken = []
            elif char == '\n':
                token = ''.join(unfinishedToken)
                codigoResaltado.append(f'<span class="comentario">{token}</span>')
                codigoResaltado.append(ESPACIO_HTML + NUEVO_PARRAFO_HTML)
                unfinishedToken = []
            elif char == ' ':
                unfinishedToken.append(ESPACIO_HTML)
            else:
                estado = "comentario_multilinea"
                unfinishedToken.append(char)
                

        elif estado == "separador":
            tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
            codigoResaltado.append(tokenEnHTML)
            unfinishedToken = []

            if char.isalpha():
                estado = "variable"
                unfinishedToken.append(char)
            elif char == '0':
                estado = "octal"
                unfinishedToken.append(char)
            elif char.isnumeric():
                estado = "entero"
                unfinishedToken.append(char)
            elif char == '.':
                estado = "real"
                unfinishedToken.append(char)
            elif char == '-':
                estado = "resta"
                unfinishedToken.append(char)
            elif char == "&#39":
                estado = "literal_caracter"
                unfinishedToken.append(char)
            elif char == '&quot':
                estado = "string"
                unfinishedToken.append(char)
            elif char == '/':
                estado = "division"
                unfinishedToken.append(char)
            elif isOperand(char):
                estado = 'operador'
                unfinishedToken.append(char)
            elif isSeparator(char):
                estado = "separador"
                unfinishedToken.append(char)
            elif char == ' ':
                estado = "inicial"
                codigoResaltado.append(ESPACIO_HTML)
            elif char == '\n':
                estado = "inicial"
                codigoResaltado.append(NUEVO_PARRAFO_HTML)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break

            
        elif estado == "string":
            if char == '&quot':
                estado = "inicial"
                unfinishedToken.append(char)
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
            else:
                unfinishedToken.append(char)


        elif estado == "literal_caracter":
            if char == '\\':
                estado = "literal_caracter_escapado"
                unfinishedToken.append(char)
            elif char == "&#39":
                codigoResaltado.append(manejarErrorSintaxis())
                break
            else:
                unfinishedToken.append(char)
                estado = "final_literal_caracter"


        elif estado == "literal_caracter_escapado":
            if char in "abfnrtv\\?" or char == "&#39" or char == "&quot":
                estado = "final_literal_caracter"
                unfinishedToken.append(char)
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break


        elif estado == "final_literal_caracter":
            if char == "&#39":
                estado = "inicial"
                unfinishedToken.append(char)
                tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
                codigoResaltado.append(tokenEnHTML)
                unfinishedToken = []
            else:
                codigoResaltado.append(manejarErrorSintaxis())
                break

    return "".join(codigoResaltado)



def generarTokenEnFormatoHTML(unfinishedTokenList):
    token = ''.join(unfinishedTokenList)
    claseCSS = generarClase(token)
    return f'<span class="{claseCSS}">{token}</span>'


def generarClase(token):

    clase = ""

    if isInteger(token):
        clase = 'literal-numerico'
    elif isHexadecimal(token):
        clase = "literal-numerico"
    elif isVariable(token):
        if token in PALABRAS_RESERVADAS:
            clase = 'palabra-reservada'
        else:
            clase = 'variable'
    elif token == "#define" or token == "#include":
        clase = 'palabra-reservada'
    elif isUnsignedOrLongInt(token):
        clase = "literal-numerico"
    elif token == '-':
        clase = 'operador'
    elif token == '/':
        clase = 'operador'
    elif isFloat(token):
        clase = 'literal-numerico'
    elif isFloatThatEndsWithF(token):
        clase = 'literal-numerico'
    elif isOperand(token):
        clase = "operador"
    elif isComment(token):
        clase = "comentario"
    elif isMultilineComment(token):
        clase = "comentario"
    elif isSeparator(token):
        clase = 'separador'
    elif isString(token) or isCharLiteral(token):
        clase="string"

    return clase


"""Recibe un string con el código ya resaltado y lo escribe
en el archivo HTML recibido
"""
def escribirCodigoResaltadoEnHTML(codigo, htmlFile):
    htmlFile.write(codigo)


def escribirInicioArchivoHTML(htmlFile):
    htmlFile.write("<!DOCTYPE html>\n")
    htmlFile.write("<html>\n")
    htmlFile.write("\t<head>\n")
    htmlFile.write("\t\t<meta charset=\"utf-8\"/>\n")
    htmlFile.write("\t\t<link rel=\"stylesheet\" href=\"styles.css\">\n")
    htmlFile.write("\t</head>\n")
    htmlFile.write("\t<body>\n")


def escribirFinalArchivoHTML(htmlFile):
    htmlFile.write("\n\t</body>\n")
    htmlFile.write("</html>")


"""Cierra los archivos y termina el programa en caso de  un error de sintaxis
"""
def manejarErrorSintaxis():
    # Escribir error en HTML y cerrar su esctructura
    return '</p>\n<p><span class="error">ERROR DE SINTAXIS</span></p>\n'


"""Recibe un token en forma de string. Regresa un booleano
que indica si el token es un operador valido
"""
def isOperand(token):
    return token in OPERADORES


"""Recibe un token en forma de string. Regresa un booleano
que indica si el token es un operador valido
"""
def isSeparator(token):
    return token in SEPARADORES


"""Recibe un token en forma de string. Regresa un booleano
que indica si el token es una variable valida
"""
def isVariable(token):

    if token.isalpha() or token.isalnum() and not isInteger(token[0]):
        return True
    elif '_' in token and token[0] != '_' and not isInteger(token[0]):
        return True

    return False


"""Recibe un token en forma de string. Regresa un booleano
que indica si el token es un entero valido
"""
def isInteger(token):
    try:
        int(token)
        return True
    except ValueError:
        return False


def isHexadecimal(token):
    if token[0:2] == "0x" or token[0:2] == "0X":
        try:
            int(token[2:], 16)
            return True
        except ValueError:
            return False

    return False


"""Recibe un token en forma de string. Regresa un booleano
que indica si el token es un numero decimal valido
"""
def isFloat(token):
    try:
        float(token)
        return True
    except ValueError:
        return False


def isFloatThatEndsWithF(token):
    if len(token) < 2:
        return False
    if token[-1] == 'F' or token[-1] == 'f':
        try:
            float(token[:-1])
            return True
        except ValueError:
            return False
    return False


def isUnsignedOrLongInt(token):
    aux = ""
    for char in token:
        if char.isnumeric():
            aux += char
        elif char in "eE+-":
            aux += char
        elif char in 'lLuU':
            continue
        else:
            return False

    # La implementación de python (a comparación de C), establece que los
    # enteros con exponente E realmente son floats. Primero hay que convertir a
    # float y luego ver si es int o no
    if isFloat(aux):
        return isInteger(float(aux))

    return False


"""Recibe un token en forma de string. Regresa un booleano
que indica si el token es un comentario
"""
def isComment(token):
    if len(token) < 2:
        return False
    return token[0:2] == "//"


def isMultilineComment(token):
    if len(token) < 4:
        return False
    return token[0:2] == "/*" or token[-2:] == "*/"


def isString(token):
    if len(token) < 2:
        return False
    return token[0:5] == "&quot" and token[-5:] == "&quot"


def isCharLiteral(token):
    if len(token) < 2:
        return False
    return token[0:4] == "&#39" and token[-4:] == "&#39"


if __name__ == '__main__':

    # Asegurarse de que el archivo fue dado en la linea de comandos
    if len(sys.argv) != 2:
        print("USO: python -m resaltadorSintaxis [ARCHIVO_CON_EJEMPLO].txt")
        sys.exit()

    archivo = sys.argv[1]

    # Asegurarse que sea un archivo .txt
    if archivo[-4:] != ".txt":
        print("ERROR: Debe proveer un archivo .txt")
        sys.exit()

    # Asegurarse de que el archivo exista en el directorio
    if not os.path.isfile(archivo):
        print ("ERROR: Este archivo no se encuentra en el directorio actual")
        sys.exit()

    resaltadorSintaxis(archivo)