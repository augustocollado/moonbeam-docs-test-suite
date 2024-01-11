import os
import unittest
from substrateinterface import SubstrateInterface, Keypair, KeypairType
from substrateinterface.exceptions import SubstrateRequestException

class TestSigningAndTransactions(unittest.TestCase):
    def setUp(self):

        # Construct the API provider
        self.ws_provider = SubstrateInterface(
            url="ws://127.0.0.1:9944",
        )  

        self.destination = "0x28aa49cc9Ee28cBb4b664356DC572A9A2AAb46e2"

        # Define the shortform private key of the sending account (Alice's)
        privatekey = bytes.fromhex("5fb92d6e98884f76de468fa3f6278f8807c48bebc13595d45af5bdc4da702133")

        # Generate the keypair
        self.keypair = Keypair.create_from_private_key(privatekey, crypto_type=KeypairType.ECDSA)

    ### TESTS ###
    def test_forming_and_sending_a_transaction(self):
        ws_provider = self.ws_provider
        keypair = self.keypair
        destination = self.destination
        
        # Form a transaction call
        call = ws_provider.compose_call(
            call_module="Balances",
            call_function="transfer_allow_death",
            call_params={
                "dest": destination,
                "value": 1 * 10**18,
            },
        )

        # Form a signed extrinsic
        extrinsic = ws_provider.create_signed_extrinsic(call=call, keypair=keypair)

        # Submit the extrinsic
        try:
            receipt = ws_provider.submit_extrinsic(extrinsic, wait_for_inclusion=True)
            
            account_info = ws_provider.query(
                module="System",
                storage_function="Account",
                params=[destination],
            )

            self.assertTrue(account_info.value["data"]["free"] >= 1 * 10**18)
            
        except SubstrateRequestException as e:
            self.fail("Submitting a signed transaction failed")

    def test_offline_signing(self):
        ws_provider = self.ws_provider
        keypair = self.keypair
        destination = self.destination

        # 1. Offline payload generation step

        # Construct a transaction call
        call = ws_provider.compose_call(
            call_module="Balances",
            call_function="transfer_allow_death",
            call_params={
                "dest": destination,
                "value": 1 * 10**18,
            },
        )

        # Generate the signature payload
        signature_payload = ws_provider.generate_signature_payload(call=call)

        # 2. Offline signing step

        # Sign the signature_payload 
        signature = keypair.sign(signature_payload)

        # 3. Online execution step

        # Construct the same transaction call that was signed
        call = ws_provider.compose_call(
            call_module="Balances",
            call_function="transfer_allow_death",
            call_params={
                "dest": destination,
                "value": 1 * 10**18,
            },
        )

        # Construct the signed extrinsic with the generated signature
        extrinsic = ws_provider.create_signed_extrinsic(
            call=call, keypair=keypair, signature=signature
        )

        # Submit the signed extrinsic
        result = ws_provider.submit_extrinsic(extrinsic=extrinsic)

        # # Check the transfer execution

        account_info = ws_provider.query(
            module="System",
            storage_function="Account",
            params=[destination],
        )
        self.assertTrue(account_info.value["data"]["free"] >= 1 * 10**18)


    def tearDown(self) -> None:
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
