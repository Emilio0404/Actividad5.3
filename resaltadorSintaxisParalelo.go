package main

import (
	"fmt"
	"os"
)

func main() {
	revisarArchivosRecibidos(os.Args[1:])

}

// Asegurarse de que el archivo fue dado en la linea de comandos y su formato es correcto
func revisarArchivosRecibidos(archivos []string) {
	noArgumentos := len(archivos)

	if noArgumentos < 1 {
		fmt.Println("ERROR: DEBE PROVEER AL MENOS UN ARCHIVO DE TEXTO")
		os.Exit(1)
	}

	for i := 0; i < noArgumentos; i++ {
		extensionArchivo := archivos[i][len(archivos[i])-4:]
		if extensionArchivo != ".txt" {
			fmt.Println("ERROR: LOS ARCHIVOS DEBEN SER .TXT")
			os.Exit(1)
		}
	}

	directorioActual, err := os.Getwd()
	if err != nil {
		fmt.Println(err)
		os.Exit(2)
	}

	// Asegurarse de que los archivos existan
	for i := 0; i < noArgumentos; i++ {
		_, err := os.Stat(directorioActual + "\\" + archivos[i])
		if os.IsNotExist(err) {
			fmt.Println("ERROR: DEBE PROVEER ARCHIVOS EXISTENTES")
			os.Exit(3)
		}
	}
}
