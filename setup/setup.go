// script to deploy the verifier smart contract and the application smart contract
// on TestNet; will write the appId of the application smart contract to file at
// the package const `appIdPath`
// Run with `go run setup.go` from its directory
package main

import (
	"log"
	"os"
	"path/filepath"
	"strconv"

	"github.com/consensys/gnark-crypto/ecc"

	"github.com/giuliop/whitelist-example-algoplonk/circuit"

	ap "github.com/giuliop/algoplonk"
	"github.com/giuliop/algoplonk/setup"
	"github.com/giuliop/algoplonk/testutils"
	sdk "github.com/giuliop/algoplonk/testutils/algosdkwrapper"
	"github.com/giuliop/algoplonk/verifier"
)

const (
	curve            = ecc.BN254
	baseDir          = ".."
	artefactsDir     = "generated"
	mainContractName = "MainContract"
)

var (
	artefactsDirPath = filepath.Join(baseDir, artefactsDir)
	mainContractPath = filepath.Join(baseDir, mainContractName+".py")
	appIdPath        = filepath.Join(artefactsDirPath, "MainContractAppId")
	verifierIdPath   = filepath.Join(artefactsDirPath, "VerifierAppId")
)

func main() {
	verifierAppId := setupVerifier()
	mainContractAppId := setupMainContract(verifierAppId)
	log.Printf("Deployed %s with appId %d", mainContractName, mainContractAppId)
}

// setupVerifierApps compiles the circuits and deploys the verifier app to TestNet
func setupVerifier() (appId uint64) {

	verifierName := verifier.VerifierContractName
	verifierPath := filepath.Join(artefactsDirPath, verifierName+".py")

	compiledCircuit, err := ap.Compile(&circuit.Circuit{}, curve, setup.Trusted)
	if err != nil {
		log.Fatalf("Error compiling circuit: %v", err)
	}

	err = compiledCircuit.WritePuyaPyVerifier(verifierPath)
	if err != nil {
		log.Fatalf("Error writing verifier: %v", err)
	}

	err = testutils.CompileWithPuyaPy(verifierPath, "")
	if err != nil {
		log.Fatalf("Error compiling with puyapy: %v", err)
	}

	err = testutils.RenamePuyaPyOutput(verifier.VerifierContractName,
		verifierName, artefactsDirPath)
	if err != nil {
		log.Fatalf("Error renaming %s: %v", verifierName, err)
	}

	appId, err = sdk.DeployArc4AppIfNeeded(verifierName, artefactsDirPath)
	if err != nil {
		log.Fatalf("Error deploying %s: %v", verifierName, err)
	}
	log.Printf("Deployed %s with appId %d", verifierName, appId)

	err = os.WriteFile(verifierIdPath, []byte(strconv.FormatUint(appId, 10)), 0644)
	if err != nil {
		log.Fatalf("Error writing verifier appId to file: %v", err)
	}

	return appId
}

// setupMainContract compiles the main contract, deploys it to Testnet, and
// writes the main contract appId to file at the package const `appIdPath`
func setupMainContract(verifierAppId uint64) (appId uint64) {

	err := testutils.CompileWithPuyaPy(mainContractPath,
		"--out-dir="+artefactsDir)
	if err != nil {
		log.Fatalf("Error compiling main contract: %v", err)
	}
	mainContractTmplSubs := map[string]string{
		"TMPL_VERIFIER_APP_ID": strconv.FormatUint(verifierAppId, 10),
	}
	tealPath := filepath.Join(artefactsDirPath, mainContractName+".approval.teal")
	err = testutils.Substitute(tealPath, mainContractTmplSubs)
	if err != nil {
		log.Fatalf("Error substituting main contract template: %v", err)
	}

	appId, err = sdk.DeployArc4AppIfNeeded(mainContractName, artefactsDirPath)
	if err != nil {
		log.Fatalf("Error deploying main contract: %v", err)
	}

	// write the appId to file "../generated/appId.txt"
	err = os.WriteFile(appIdPath, []byte(strconv.FormatUint(appId, 10)), 0644)
	if err != nil {
		log.Fatalf("Error writing application appId to file: %v", err)
	}

	return appId
}

func GetSchema() *sdk.Arc32Schema {
	schema, err := sdk.ReadArc32Schema(
		filepath.Join(artefactsDir, mainContractName+".arc32.json"))
	if err != nil {
		log.Fatalf("Error reading main contract schema: %v", err)
	}
	return schema
}
