package main

import (
	"fmt"
	"io"
	"os"
	"strconv"
	"strings"
	"unicode"
)

var PALABRAS_RESERVADAS = []string{
	"auto", "else", "long", "switch", "break", "enum", "register",
	"typedef", "case", "extern", "return", "union", "char", "float",
	"short", "unsigned", "const", "for", "signed", "void", "continue",
	"goto", "sizeof", "volatile", "default", "if", "static", "while",
	"do", "int", "struct", "double", "main"}

var SEPARADORES = []string{
	"{", "}", "(", ")", "[", "]", ",", ";"}

var OPERADORES = []string{
	"+", "*", "%", "=", ">", "<", "!", "&", "?", ":", "~", "^",
	"|", "&lt", "&gt", "&amp", "."}

var CHAR_REQUIERE_FORMATO = map[string]string{
	"&":  "&amp",
	"<":  "&lt",
	">":  "&gt",
	"\"": "&quot",
	"'":  "&#39"}

func main() {
	nombresArchivos := os.Args[1:]
	noArgumentos := len(nombresArchivos)
	if noArgumentos < 1 {
		fmt.Println("ERROR: DEBE PROVEER AL MENOS UN ARCHIVO DE TEXTO")
		os.Exit(1)
	}

	directorioActual := obtenerDirectorioActual()

	for i := 0; i < noArgumentos; i++ {
		if !revisarFormatoArchivo(nombresArchivos[i]) {
			fmt.Println("ERROR: LOS ARCHIVOS DEBEN SER .TXT")
			os.Exit(3)
		}

		if !archivoExiste(nombresArchivos[i], directorioActual) {
			fmt.Println("ERROR: DEBE PROVEER ARCHIVOS EXISTENTES")
			os.Exit(4)
		}
	}

	for i := 0; i < noArgumentos; i++ {
		resaltadorSintaxis(nombresArchivos[i])
	}
}

func obtenerDirectorioActual() string {
	directorioActual, err := os.Getwd()
	if err != nil {
		fmt.Println(err)
		os.Exit(2)
	}
	return directorioActual
}

func revisarFormatoArchivo(archivo string) bool {
	if len(archivo) < 4 {
		return false
	}
	return archivo[len(archivo)-4:] == ".txt"
}

func archivoExiste(archivo string, directorioActual string) bool {
	_, err := os.Stat(directorioActual + "\\" + archivo)
	if os.IsNotExist(err) {
		return false
	}
	return true
}

func resaltadorSintaxis(archivo string) {
	// Crear archivo HTML
	nombreArchivoHTML := crearArchivoHTML(archivo)
	archivoHTML, err := os.Open(nombreArchivoHTML)
	check_error(err)
	defer archivoHTML.Close()

	codigoResaltado := "<!DOCTYPE html>\n<html>\n\t<head>\n\t\t<meta charset=\"utf-8\"/>\n\t\t<link rel=\"stylesheet\" href=\"styles.css\">\n\t</head>\n\t<body>\n"
	codigoResaltado += resaltar(archivo)
	codigoResaltado += "\n\t</body>\n</html>"

	escribirCodigoResaltado(nombreArchivoHTML, codigoResaltado)
}

// Crea un archivo HTML con el nombre de archivo que recibe. Si el
// archivo ya existe, lo limpia
func crearArchivoHTML(archivo string) string {
	nombreArchivoHTML := archivo[:len(archivo)-4] + ".html"

	if archivoExiste(nombreArchivoHTML, obtenerDirectorioActual()) {
		err := os.Truncate(nombreArchivoHTML, 0)
		check_error(err)
	} else {
		archivoHTML, err := os.Create(nombreArchivoHTML)
		check_error(err)
		defer archivoHTML.Close()
	}

	return nombreArchivoHTML
}

func resaltar(archivo string) string {

	NUEVO_PARRAFO_HTML := "</p>\n\t\t<p>"
	ESPACIO_HTML := "&nbsp;"

	codigoResaltado := "\t\t<p>"
	var unfinishedToken []string

	estado := "inicial"
	tokenEnHTML := ""

	// Se lee el txt hasta que se acaben los caracteres
	f, err := os.Open(archivo)
	check_error(err)
	defer f.Close()

	buffer := make([]byte, 1)
	for {
		// Leer caracter
		_, err := f.Read(buffer)
		check_error(err)

		// Si no se leyo ningun caracter, resaltar token y agregarlo al codigo
		if err == io.EOF {
			tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
			codigoResaltado += tokenEnHTML + "</p>"
			break
		}

		char := string(buffer)

		if stringInMap(char, CHAR_REQUIERE_FORMATO) {
			char = CHAR_REQUIERE_FORMATO[char]
		}

		if estado == "inicial" {
			if isAlpha(char) {
				estado = "variable"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "0" {
				estado = "octal"
				unfinishedToken = append(unfinishedToken, char)
			} else if isNumeric(char) {
				estado = "entero"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "." {
				estado = "real_sin_parte_entera"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "-" {
				estado = "resta"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "&#39" {
				estado = "literal_caracter"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "&quot" {
				estado = "string"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "/" {
				estado = "division"
				unfinishedToken = append(unfinishedToken, char)
			} else if isOperand(char) {
				estado = "operador"
				unfinishedToken = append(unfinishedToken, char)
			} else if isSeparator(char) {
				estado = "separador"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == " " {
				estado = "inicial"
				codigoResaltado += ESPACIO_HTML
			} else if char == "\n" {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado = codigoResaltado + tokenEnHTML + ESPACIO_HTML + NUEVO_PARRAFO_HTML
				unfinishedToken = nil
			} else if char == "#" {
				estado = "include_define"
				unfinishedToken = append(unfinishedToken, char)
			} else {
				codigoResaltado += manejarErrorSintaxis()
				break
			}

		} else if estado == "include_define" {
			if char == " " {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado = codigoResaltado + tokenEnHTML + ESPACIO_HTML
				unfinishedToken = nil
			} else if char == "\n" {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado = codigoResaltado + tokenEnHTML + ESPACIO_HTML + NUEVO_PARRAFO_HTML
				unfinishedToken = nil
			} else if isAlpha(char) {
				unfinishedToken = append(unfinishedToken, char)
			} else {
				codigoResaltado += manejarErrorSintaxis()
				break
			}

		} else if estado == "variable" {
			if isAlpha(char) || isNumeric(char) || char == "_" {
				estado = "variable"
				unfinishedToken = append(unfinishedToken, char)
			} else {
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil

				if char == "/" {
					estado = "division"
					unfinishedToken = append(unfinishedToken, char)
				} else if char == "-" {
					estado = "resta"
					unfinishedToken = append(unfinishedToken, char)
				} else if isSeparator(char) {
					estado = "separador"
					unfinishedToken = append(unfinishedToken, char)
				} else if char == "." {
					estado = "operador"
					unfinishedToken = append(unfinishedToken, char)
				} else if isOperand(char) {
					estado = "operador"
					unfinishedToken = append(unfinishedToken, char)
				} else if char == " " {
					estado = "inicial"
					codigoResaltado += ESPACIO_HTML
				} else if char == "/n" {
					estado = "inicial"
					codigoResaltado += NUEVO_PARRAFO_HTML
				} else {
					codigoResaltado += manejarErrorSintaxis()
					break
				}
			}

		} else if estado == "entero" {
			if isNumeric(char) {
				estado = "entero"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "e" || char == "E" {
				estado = "entero_con_exponente"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "u" || char == "U" {
				estado = "unsigned_int"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "l" || char == "L" {
				estado = "long_int"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "." {
				estado = "real"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "-" {
				estado = "resta"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "/" {
				estado = "division"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if isOperand(char) {
				estado = "operador"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if isSeparator(char) {
				estado = "separador"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if char == " " {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += (tokenEnHTML + ESPACIO_HTML)
				unfinishedToken = nil
			} else if char == "\n" {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += (tokenEnHTML + NUEVO_PARRAFO_HTML)
				unfinishedToken = nil
			} else {
				codigoResaltado += manejarErrorSintaxis()
				break
			}

		} else if estado == "entero_con_exponente" {
			// Si recibe una E, se asegura de que el siguiente caracter sea entero o -
			if isNumeric(char) {
				unfinishedToken = append(unfinishedToken, char)
				estado = "entero_con_exponente_aux1"
			} else if char == "-" || char == "+" {
				unfinishedToken = append(unfinishedToken, char)
				estado = "entero_con_exponente_aux2"
			} else {
				codigoResaltado += manejarErrorSintaxis()
				break
			}

		} else if estado == "entero_con_exponente_aux1" {
			// Es valido para salir de numero real despues de recibir E o E-
			if isNumeric(char) {
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "u" || char == "U" {
				estado = "unsigned_int"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "l" || char == "L" {
				estado = "long_int"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "-" {
				estado = "resta"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "/" {
				estado = "division"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if isOperand(char) {
				estado = "operador"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if isSeparator(char) {
				estado = "separador"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if char == " " {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += (tokenEnHTML + ESPACIO_HTML)
				unfinishedToken = nil
			} else if char == "\n" {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += (tokenEnHTML + NUEVO_PARRAFO_HTML)
				unfinishedToken = nil
			} else {
				codigoResaltado += manejarErrorSintaxis()
				break
			}

		} else if estado == "entero_con_exponente_aux2" {
			// Se asegura que despues de recibir un E- o E+, se reciba un numero
			if isNumeric(char) {
				unfinishedToken = append(unfinishedToken, char)
				estado = "entero_con_exponente_aux1"
			} else {
				codigoResaltado += manejarErrorSintaxis()
				break
			}

		} else if estado == "unsigned_int" {
			if char == "l" || char == "L" {
				estado = "unsigned_int_long"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "-" {
				estado = "resta"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "/" {
				estado = "division"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if isOperand(char) {
				estado = "operador"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if isSeparator(char) {
				estado = "separador"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if char == " " {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += (tokenEnHTML + ESPACIO_HTML)
				unfinishedToken = nil
			} else if char == "\n" {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += (tokenEnHTML + NUEVO_PARRAFO_HTML)
				unfinishedToken = nil
			} else {
				codigoResaltado += manejarErrorSintaxis()
				break
			}

		} else if estado == "unsigned_long_int" {
			if char == "l" || char == "L" {
				estado = "unsigned_long_long_int"
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "-" {
				estado = "resta"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if char == "/" {
				estado = "division"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if isOperand(char) {
				estado = "operador"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if isSeparator(char) {
				estado = "separador"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			} else if char == " " {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += (tokenEnHTML + ESPACIO_HTML)
				unfinishedToken = nil
			} else if char == "\n" {
				estado = "inicial"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += (tokenEnHTML + NUEVO_PARRAFO_HTML)
				unfinishedToken = nil
			} else {
				codigoResaltado += manejarErrorSintaxis()
				break
			}

		} else if estado == "unsigned_long_long_int" || estado == "long_unsigned_int" {

		} else if estado == "long_int" {

		} else if estado == "long_long_int" {

		} else if estado == "octal" {

		} else if estado == "hexadecimal" {

		} else if estado == "hexadecimal_final" {

		} else if estado == "real_sin_parte_entera" {

		} else if estado == "puede_ser_real" {

		} else if estado == "real" {

		} else if estado == "real_aux1" {

		} else if estado == "real_aux2" {

		} else if estado == "real_aux3" {

		} else if estado == "fin_real_con_f" {
			if isOperand(char) {
				estado = "operador"
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
				unfinishedToken = append(unfinishedToken, char)
			}

		} else if estado == "resta" {

		} else if estado == "division" {

		} else if estado == "operador" {

		} else if estado == "comentario" {

		} else if estado == "comentario" {

		} else if estado == "cerrar_comentario_multilinea" {

		} else if estado == "separador" {

		} else if estado == "string" {

		} else if estado == "literal_caracter" {

		} else if estado == "literal_caracter_escapado" {

		} else if estado == "final_literal_caracter" {
			if char == "&#39" {
				estado = "inicial"
				unfinishedToken = append(unfinishedToken, char)
				tokenEnHTML = generarTokenEnFormatoHTML(unfinishedToken)
				codigoResaltado += tokenEnHTML
				unfinishedToken = nil
			} else {
				codigoResaltado += manejarErrorSintaxis()
				break
			}
		}
	}

	return codigoResaltado
}

// Escribe el codigo resaltado en un archivo
func escribirCodigoResaltado(nombreArchivo string, codigoResaltado string) {
	err := os.WriteFile(nombreArchivo, []byte(codigoResaltado), 0644)
	check_error(err)
}

func generarTokenEnFormatoHTML(unfinishedTokenList []string) string {
	token := strings.Join(unfinishedTokenList, "")
	claseCSS := generarClase(token)
	return fmt.Sprintf("<span class=\"%s\">%s</span>", claseCSS, token)
}

func generarClase(token string) string {

	clase := ""

	if isInteger(token) {
		clase = "literal-numerico"
	} else if isHexadecimal(token) {
		clase = "literal-numerico"
	} else if isVariable(token) {
		if stringInSlice(token, PALABRAS_RESERVADAS) {
			clase = "palabra-reservada"
		} else {
			clase = "variable"
		}
	} else if token == "#define" || token == "#include" {
		clase = "palabra-reservada"
	} else if isUnsignedOrLongInt(token) {
		clase = "literal-numerico"
	} else if token == "-" {
		clase = "operador"
	} else if token == "/" {
		clase = "operador"
	} else if isFloat(token) {
		clase = "literal-numerico"
	} else if isFloatThatEndsWithF(token) {
		clase = "literal-numerico"
	} else if isOperand(token) {
		clase = "operador"
	} else if isComment(token) {
		clase = "comentario"
	} else if isMultilineComment(token) {
		clase = "comentario"
	} else if isSeparator(token) {
		clase = "separador"
	} else if isString(token) || isCharLiteral(token) {
		clase = "string"
	}

	return clase
}

func isAlpha(s string) bool {
	for _, r := range s {
		if !unicode.IsLetter(r) {
			return false
		}
	}
	return true
}

func isNumeric(s string) bool {
	_, err := strconv.Atoi(s)
	if err != nil {
		return false
	}
	return true
}

func isOperand(token string) bool {
	return stringInSlice(token, OPERADORES)
}

func isSeparator(token string) bool {
	return stringInSlice(token, SEPARADORES)
}

func isVariable(token string) bool {
	if token[0] == '_' {
		token = token[1:]
	}

	for i, char := range token {
		if i == 0 && unicode.IsNumber(char) {
			return false
		}
		if !(unicode.IsNumber(char) || unicode.IsLetter(char)) {
			return false
		}
	}
	return true
}

func manejarErrorSintaxis() string {
	return "</p>\n<p><span class=\"error\">ERROR DE SINTAXIS</span></p>\n"
}

func isComment(token string) bool {
	if len(token) < 2 {
		return false
	}
	return token[0:2] == "//"
}

func isMultilineComment(token string) bool {
	if len(token) < 2 {
		return false
	}
	return token[0:2] == "/*" || token[len(token)-2:] == "/*"
}

func isString(token string) bool {
	if len(token) < 2 {
		return false
	}
	return token[0:5] == "&quot" && token[len(token)-5:] == "&quot"
}

func isCharLiteral(token string) bool {
	if len(token) < 2 {
		return false
	}
	return token[0:4] == "&#39" && token[len(token)-4:] == "&#39"
}

func stringInSlice(a string, list []string) bool {
	for _, b := range list {
		if b == a {
			return true
		}
	}
	return false
}

func stringInMap(a string, m map[string]string) bool {
	if _, exists := m[a]; exists {
		return true
	}
	return false
}

func check_error(e error) {
	if e == io.EOF {
		return
	} else if e != nil {
		fmt.Println(e)
	}
}
