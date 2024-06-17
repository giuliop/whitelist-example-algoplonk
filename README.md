## Whitelist - a zero-knowledge application example on the Algorand TestNet

As requested by the community, we have deployed a simple example of a zk application on the Algorand TestNet using the [AlgoPlonk](https://github.com/giuliop/algoplonk) toolchain.
<br>
The application let users, who know a secret word, register their address on a whitelist.
<br>
To prove to the application that they know the secret without revealing it publicly, they submit a zero knowledge proof that the application verifies on chain.

This is an example for developers looking to learn more about how to use [AlgoPlonk](https://github.com/giuliop/algoplonk), not for users, so no web frontend is provided, only a command line script to interact with the application.

Let's explain how the application works and then discuss further technical details.

### How it works

The application is composed of two smart contracts on chain:
* the main contract ('app') with app id 682246016
* the verifier contract ('verifier') with app id 682246002

We'll discuss in the next section how they were generated, let's focus now on how to use them.

The app abi offers these [arc4](https://github.com/algorandfoundation/ARCs/blob/main/ARCs/arc-0004.md) methods to users (beyond admin ones for the creator):
* `opt_in_or_out() -> None`

* `is_on_whitelist(address: Address) -> Bool`

* `add_address_to_whitelist(address: Bytes32, proof: DynamicArray[Bytes32]) -> String`

The first one is a basic opt-in / opt-out method, needed because the application uses local storage to register an address on the whitelist.
<br>The second simply returns whether an address is on the whitelist.
<br>The third is the key one, it allows the user to register an address to the whitelist by submitting the address and the zk proof. The method returns an error message or an empty string on success.

Registering an address is a two step process:
1. Generate the proof with AlgoPlonk and save it to file using the save_proof.go script by running `go run save_proof.go <address> <secret_word>`, where address is an Algorand address like JIKHN6HXB2B4GA3OAWZSOAKNWVPXWWB7S6VPPD4N6TEAJQNO2KP6EMHFUU and the secret word can be found in the `circuit/circuit.go file` :)
<br>This will export the proof and public inputs to file in the `generated` folder to be later sent on chain. In reality we will need only the proof file since we will be submitting the single public input, the address to register, as a transaction argument.
<br>You can try to generate proofs with the wrong secret word which will of course fail. To create a "wrong" proof to submit to the network and see the verification fail, you can manually modify a byte in a good proof and send that.

2. Now we can call the `add_address_to_whitelist` app method.
<br>The `main.py` script does exactly that, using the account and Algorand node details in the `.env` file, to be setup before running the `main.py` script.
<br>Check the file `.env.template` as an example of how to write the `.env` file, which is not tracked by being in `.gitignore`.

That's it, let's discuss now some technical details.

### More technical details

File `circuit/circuit.go` contains the circuit definition; it's a simple circuit that embeds the hash of the secret word and accepts two inputs: the public input `Address` to simply bind it to the proof and the private input `SecretWord` which the circuit will hash and compare to the correct hash to verify the proof.

While `circuit.go` shows the secret word in the clear for educational purposes, in a real case scenario it would only embed the hashed value so that it could be made open source without revealing anything.

File `setup/setup.go` was run with `go run setup.go` to:
1. Compile the circuit, create a smart contract verifier with AlgoPlonk, and deploy it to TestNet

2. Compile the main application smart contract defined in `MainContract.py`, embedding the app id of the deployed verifier, and deploy it to TestNet as well.

The main app is defined in `MainContract.py` (let's the lord of programmers be praised for Algokit and python on Algorand :) and makes an inner transaction call to the on-chain verifier to verify the zk proof. The verifier expects a proof and its public inputs and the main app gets the proof from the outer call and builds the public inputs from the passed-in `address` parameter. That's pretty typical in zk application since you generally need to make checks and take actions based on the public inputs.

The proof is saved to file by AlgoPlonk which wraps [gnark](https://github.com/Consensys/gnark) for circuit compilation and proof generation.
The script in `main.py` reads it from file and passes it to the main app as a `DynamicArray[Bytes32]` where `Bytes32` is a `StaticArray` of 32 `Bytes`.

One last thing: the prover and the verifier need to be follow the exact same protocol, which means that gnark, which we wrap to create the proofs, and AlgoPlonk, which generates the smart contracts verifiers, need to be in sync.
The current commit, v0.2, uses AlgoPlonk v0.1.5, which wraps gnark v0.10.0.
The previous tagged commit, v0.1, uses AlgoPlonk v0.1.4, which wraps gnark v0.9.0, and was deployed to a different set of smart contract on TestNet (see that commit README).

---

By studying this handful of short files you should get a good sense of how to build and deploy simple zk application on Algorand !

Let us know for any question or feedback.

And by the way, why do I keep talking in plural? 🤪
