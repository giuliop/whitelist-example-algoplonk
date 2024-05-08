from dotenv import load_dotenv
import os
from pathlib import Path
import sys

import algosdk as sdk
from algosdk import atomic_transaction_composer as atomic

import algokit_utils as ak


### SET CONFIGURATION ###
proof_path = "generated/proof"

load_dotenv() # read "SIGNER_ADDRESS" and "SIGNER_MNEMONIC" from .env file
signer_address = os.getenv("SIGNER_ADDRESS")
signer_mnemonic = os.getenv("SIGNER_MNEMONIC")
if not signer_address or not signer_mnemonic:
    print("Please provide a signer address and mnemonic in the .env file.\n"
          "Check file .env.template for an example.")

try:
    signer_private_key = sdk.mnemonic.to_private_key(signer_mnemonic)
except Exception as e:
    print("Invalid mnemonic provided in the .env file:", e)
    sys.exit(1)

signer = atomic.AccountTransactionSigner(signer_private_key)
algod_client = ak.get_algod_client()

with open("generated/MainContractAppId", "r") as file:
    application_app_id = int(file.read())

with open ("generated/VerifierAppId", "r") as file:
    verifier_app_id = int(file.read())

app_client = ak.ApplicationClient(
    algod_client=algod_client,
    app_spec=Path("generated/MainContract.arc32.json"),
    app_id=application_app_id,
    signer=signer,
)


def main():
    # if needed, opt in the signer address to the application
    if not is_opted_in(signer_address):
        print("Opting in to the application...\n")
        app_client.opt_in(call_abi_method="opt_in_or_out")

    print("Adding address to the whitelist...\n")

    error_result = add_to_whitelist(signer_address)
    if error_result:
        print("The contract returned an error trying to add to whitelist:\n",
               error_result, "\n")

    elif is_on_whitelist(signer_address):
        print("Address added to the whitelist !\n")

    else:
        print("Unexpected error: contract did not return an error but address "
              "not added to the whitelist\n")


def add_to_whitelist(address: str) -> str:
    # read the proof from file, you need to have generated it previously with
    # `go run save_proof.go <address> <secret_word>`
    with open(proof_path, "br") as file:
        proof = file.read()
        # split the proof into 32-byte chunks, as expected by the contract
        abi_proof = [proof[i:i+32] for i in range(0, len(proof), 32)]

    # we don't need to read the public inputs from file, we will build them in
    # the smart contract from the address parameter, the only public input
    abi_address = sdk.encoding.decode_address(address)

    # verifying is expensive :)
    sp = algod_client.suggested_params()
    sp.flat_fee = True
    sp.fee = sdk.constants.min_txn_fee * 220

    error_result = app_client.call(
        call_abi_method="add_address_to_whitelist",
        transaction_parameters=ak.TransactionParameters(
            suggested_params=sp,
            foreign_apps=[verifier_app_id],
        ),
        address=abi_address,
        proof=abi_proof,
    ).return_value

    return error_result


def is_on_whitelist(address: str) -> bool:
    return app_client.call(
        call_abi_method="is_on_whitelist",
        transaction_parameters=ak.TransactionParameters(
            accounts=[address],
        ),
        address=address,
    ).return_value


def is_opted_in(address: str) -> bool:
    info = algod_client.account_info(address)
    for app in info.get('apps-local-state', []):
        if app['id'] == application_app_id:
            return True
    return False

if __name__ == "__main__":
    main()
