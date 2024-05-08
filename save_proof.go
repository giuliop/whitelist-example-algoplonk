package main

import (
	"flag"
	"fmt"
	"log"

	"github.com/algorand/go-algorand-sdk/v2/types"
	ap "github.com/giuliop/algoplonk"
	"github.com/giuliop/algoplonk/setup"
	"github.com/giuliop/whitelist-example-algoplonk/circuit"
)

const (
	proofPath        = "generated/proof"
	publicInputsPath = "generated/public_inputs"
)

var commandHelp = `Call with
	go run save_proof.go <address> <secret_word>
to generate a proof to add 'address' to the whitelist, and save to file the
proof and public inputs in generated/proof and generated/public_inputs
`

func main() {
	flag.Parse()
	args := flag.Args()
	if len(args) != 2 {
		fmt.Println(commandHelp)
		return
	}

	addressString := args[0]
	secretword := args[1]

	address, err := types.DecodeAddress(addressString)
	if err != nil {
		log.Fatalln("Error decoding address:", err)
	}

	cc, err := ap.Compile(&circuit.Circuit{}, circuit.Curve, setup.Trusted)
	if err != nil {
		log.Fatalln("Error compiling circuit:", err)
	}
	vp, err := cc.Verify(&circuit.Circuit{Address: address[:],
		SecretWord: []byte(secretword)})
	if err != nil {
		log.Fatalln("Error generating proof: ", err)
	}
	vp.ExportProofAndPublicInputs(proofPath, publicInputsPath)
}
