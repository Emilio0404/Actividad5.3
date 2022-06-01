package main

import (
	"fmt"
	"io"
	"os"
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

	directorioActual, err := os.Getwd()
	if err != nil {
		fmt.Println(err)
		os.Exit(2)
	}

	for i := 0; i < noArgumentos; i++ {
		if !revisarFormatoArchivo(nombresArchivos[i]) {
			fmt.Println("ERROR: LOS ARCHIVOS DEBEN SER .TXT")
			os.Exit(3)
		}

		if !revisarArchivoExiste(nombresArchivos[i], directorioActual) {
			fmt.Println("ERROR: DEBE PROVEER ARCHIVOS EXISTENTES")
			os.Exit(4)
		}
	}

	for i := 0; i < noArgumentos; i++ {
		resaltadorSintaxis(nombresArchivos[i])
	}
}

func revisarFormatoArchivo(archivo string) bool {
	extensionArchivo := archivo[len(archivo)-4:]
	return extensionArchivo == ".txt"
}

func revisarArchivoExiste(archivo string, directorioActual string) bool {
	_, err := os.Stat(directorioActual + "\\" + archivo)
	if os.IsNotExist(err) {
		return false
	}

	return true
}

func resaltadorSintaxis(archivo string) {

	file, err := os.Open(archivo)
	if err != nil {
		fmt.Println("Error opening file!!!")
	}
	defer file.Close()

	const maxSz = 1

	// create buffer
	b := make([]byte, maxSz)

	for {
		// read content to buffer
		readTotal, err := file.Read(b)
		if err != nil {
			if err != io.EOF {
				fmt.Println(err)
			}
			break
		}
		fmt.Println(string(b[:readTotal])) // print content from buffer
	}
}
