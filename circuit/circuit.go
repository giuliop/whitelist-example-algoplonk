// Package circuits defines the zk-circuit for the application
package circuit

import (
	"math/big"

	"github.com/consensys/gnark-crypto/ecc"
	"github.com/consensys/gnark-crypto/ecc/bn254/fr"
	mimc_bn254 "github.com/consensys/gnark-crypto/ecc/bn254/fr/mimc"
	"github.com/consensys/gnark/frontend"
	"github.com/consensys/gnark/std/hash/mimc"
)

const (
	Curve      = ecc.BN254
	secretWord = "AlgorandDoesItBetter"
)

var HashCheck = mimcStringHash(secretWord)

type Circuit struct {
	Address    frontend.Variable `gnark:",public"`
	SecretWord frontend.Variable
}

func (c *Circuit) Define(api frontend.API) error {
	mimc, _ := mimc.NewMiMC(api)

	mimc.Write(c.SecretWord)
	hash := mimc.Sum()

	api.AssertIsEqual(hash, HashCheck)

	return nil
}

func mimcStringHash(secretWord string) []byte {
	n := new(big.Int).SetBytes([]byte(secretWord))
	n = n.Mod(n, fr.Modulus())
	mimc := mimc_bn254.NewMiMC()
	mimc.Write(n.FillBytes(make([]byte, mimc.BlockSize())))
	return mimc.Sum(nil)
}
