// script to deploy the verifier smart contract and the application smart contract
// on TestNet; will write the appId of the application smart contract to file at
// the package var `appIdPath`
// Run with `go run setup.go` from its directory
package main

import (
	"context"
	"encoding/base64"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strconv"

	"github.com/algorand/go-algorand-sdk/v2/crypto"
	"github.com/algorand/go-algorand-sdk/v2/mnemonic"
	"github.com/algorand/go-algorand-sdk/v2/transaction"
	"github.com/algorand/go-algorand-sdk/v2/types"
	"github.com/consensys/gnark-crypto/ecc"

	"github.com/algorand/go-algorand-sdk/v2/client/v2/algod"
	"github.com/joho/godotenv"

	ap "github.com/giuliop/algoplonk"
	"github.com/giuliop/algoplonk/setup"
	"github.com/giuliop/algoplonk/testutils"
	sdk "github.com/giuliop/algoplonk/testutils/algosdkwrapper"
	"github.com/giuliop/algoplonk/verifier"
	"github.com/giuliop/whitelist-example-algoplonk/circuit"
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
	envPath          = filepath.Join(baseDir, ".env")

	algodToken  string
	algodUrl    string
	algodClient *algod.Client
	signer      crypto.Account
)

func init() {
	// Load .env file
	if err := godotenv.Load(envPath); err != nil {
		log.Fatalf("Error loading .env file")
	}
	algodToken = os.Getenv("ALGOD_TOKEN")
	algodUrl = os.Getenv("ALGOD_SERVER") + ":" + os.Getenv("ALGOD_PORT")

	var err error
	algodClient, err = algod.MakeClient(algodUrl, algodToken)
	if err != nil {
		log.Fatalf("Failed to create algod client: %s", err)
	}

	signerMnemonic := os.Getenv("SIGNER_MNEMONIC")
	signerPrivateKey, err := mnemonic.ToPrivateKey(signerMnemonic)
	if err != nil {
		log.Fatalf("Failed to get private key from mnemonic: %s", err)
	}
	signer, err = crypto.AccountFromPrivateKey(signerPrivateKey)
	if err != nil {
		log.Fatalf("Failed to get account from private key: %s", err)
	}

}

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

	appId, err = deployApp(verifierName, artefactsDirPath)
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

	appId, err = deployApp(mainContractName, artefactsDirPath)
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

// deployApp deploys an application to the blockchain from the teal files in:
// `dir`/`appName`.approval.teal and `dir`/`appName`.clear.teal,
// and the arc32 schema in `dir`/`appName`.arc32.json
func deployApp(appName string, dir string) (appId uint64, err error) {
	approvalBin, err := compileTealFromFile(filepath.Join(dir,
		appName+".approval.teal"))
	if err != nil {
		return 0, fmt.Errorf("failed to read approval program: %v", err)
	}
	clearBin, err := compileTealFromFile(filepath.Join(dir,
		appName+".clear.teal"))
	if err != nil {
		return 0, fmt.Errorf("failed to read clear program: %v", err)
	}
	schema, err := sdk.ReadArc32Schema(filepath.Join(dir, appName+".arc32.json"))
	if err != nil {
		return 0, fmt.Errorf("failed to read arc32 schema: %v", err)
	}

	creator := signer
	sp, err := algodClient.SuggestedParams().Do(context.Background())
	if err != nil {
		return 0, fmt.Errorf("failed to get suggested params: %v", err)
	}
	createMethod, err := schema.Contract.GetMethodByName("create")
	if err != nil {
		return 0, fmt.Errorf("failed to get create method: %v", err)
	}
	extraPages := uint32(len(approvalBin)) / 2048
	if extraPages > 3 {
		return 0, fmt.Errorf("approval program too large even for extra pages: "+
			"%d bytes", len(approvalBin))
	}
	txn, err := transaction.MakeApplicationCreateTxWithExtraPages(
		false, approvalBin, clearBin,
		types.StateSchema{NumUint: schema.State.Global.NumUints,
			NumByteSlice: schema.State.Global.NumByteSlices},
		types.StateSchema{NumUint: schema.State.Local.NumUints,
			NumByteSlice: schema.State.Local.NumByteSlices},
		[][]byte{createMethod.GetSelector(), []byte(appName)},
		nil, nil, nil,
		sp, creator.Address, nil,
		types.Digest{}, [32]byte{}, types.ZeroAddress, extraPages,
	)
	if err != nil {
		return 0, fmt.Errorf("failed to make create txn: %v", err)
	}

	txid, stx, err := crypto.SignTransaction(creator.PrivateKey, txn)
	if err != nil {
		return 0, fmt.Errorf("failed to sign transaction: %v", err)
	}
	_, err = algodClient.SendRawTransaction(stx).Do(context.Background())
	if err != nil {
		return 0, fmt.Errorf("failed to send transaction: %v", err)
	}
	confirmedTxn, err := transaction.WaitForConfirmation(algodClient, txid,
		4, context.Background())
	if err != nil {
		return 0, fmt.Errorf("error waiting for confirmation:  %v", err)
	}

	fmt.Printf("App %s created with id %d\n", appName,
		confirmedTxn.ApplicationIndex)

	return confirmedTxn.ApplicationIndex, nil
}

// compileTealFromFile reads a teal file and returns a compiled b64 binary.
func compileTealFromFile(tealFile string) ([]byte, error) {
	teal, err := os.ReadFile(tealFile)
	if err != nil {
		return nil, fmt.Errorf("failed to read %s from file: %v", tealFile, err)
	}

	result, err := algodClient.TealCompile(teal).Do(context.Background())
	if err != nil {
		return nil, fmt.Errorf("failed to compile %s: %v", tealFile, err)
	}
	binary, err := base64.StdEncoding.DecodeString(result.Result)
	if err != nil {
		log.Fatalf("failed to decode approval program: %v", err)
	}

	return binary, nil
}
