package main

import (
	"fmt"
	"os"
	"strings"
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
	codigoResaltado += resaltar()
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

func resaltar() string {
	return "hello world"
}

// Escribe el codigo resaltado en un archivo
func escribirCodigoResaltado(nombreArchivo string, codigoResaltado string) {
	err := os.WriteFile(nombreArchivo, []byte(codigoResaltado), 0644)
	check_error(err)
}

func check_error(e error) {
	if e != nil {
		fmt.Println(e)
	}
}

func generarTokenEnFormatoHTML(unfinishedTokenList []string) string {
	token := strings.Join(unfinishedTokenList, "")
	claseCSS := generarClase(token)
	return "<span class=" + claseCSS + ">" + "token" + "</span>"
}

func generarClase(token string) string {

	var clase string = ""

	if isInteger(token) {
		clase = "literal-numerico"
	} else if isHexadecimal(token) {
		clase = "literal-numerico"
	} else if isVariable(token) {
		// aqui puedo usar un método de find, pero funciona con slices. creo que si se debe de poder.

		for _, v := range PALABRAS_RESERVADAS {
			if v == token {
				clase = "palabra-reservada"
			}
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
		clase = "seprador"
	} else if isString(token) || isCharLiteral(token) {
		clase = "string"
	}

	return clase

}
