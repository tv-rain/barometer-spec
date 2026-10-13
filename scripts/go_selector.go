// Resolve declarations without compiling or executing the inspected source.
package main

import (
	"encoding/json"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
)

type request struct {
	Source string `json:"source"`
	Symbol string `json:"symbol"`
}

type response struct {
	Matches int    `json:"matches"`
	Error   string `json:"error"`
}

func receiver(expr ast.Expr) string {
	switch value := expr.(type) {
	case *ast.Ident:
		return value.Name
	case *ast.StarExpr:
		return receiver(value.X)
	case *ast.IndexExpr:
		return receiver(value.X)
	case *ast.IndexListExpr:
		return receiver(value.X)
	}
	return ""
}

func resolve(input request) response {
	file, err := parser.ParseFile(token.NewFileSet(), "selected.go", input.Source, 0)
	if err != nil {
		return response{Error: "selected source is not valid Go syntax"}
	}
	result := response{}
	add := func(name string) {
		if name == input.Symbol {
			result.Matches++
		}
	}
	for _, declaration := range file.Decls {
		switch value := declaration.(type) {
		case *ast.FuncDecl:
			if value.Recv == nil {
				add(value.Name.Name)
			} else if len(value.Recv.List) == 1 {
				add(receiver(value.Recv.List[0].Type) + "." + value.Name.Name)
			}
		case *ast.GenDecl:
			for _, spec := range value.Specs {
				switch named := spec.(type) {
				case *ast.TypeSpec:
					add(named.Name.Name)
					var fields *ast.FieldList
					switch body := named.Type.(type) {
					case *ast.StructType:
						fields = body.Fields
					case *ast.InterfaceType:
						fields = body.Methods
					}
					if fields != nil {
						for _, field := range fields.List {
							for _, name := range field.Names {
								add(named.Name.Name + "." + name.Name)
							}
						}
					}
				case *ast.ValueSpec:
					for _, name := range named.Names {
						add(name.Name)
					}
				}
			}
		}
	}
	return result
}

func main() {
	var input request
	if json.NewDecoder(os.Stdin).Decode(&input) != nil {
		os.Exit(2)
	}
	if json.NewEncoder(os.Stdout).Encode(resolve(input)) != nil {
		os.Exit(2)
	}
}
