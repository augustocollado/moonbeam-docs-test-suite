import unittest
from dotenv import load_dotenv
from substrateinterface import SubstrateInterface

load_dotenv()

class TestQueryingForinformation(unittest.TestCase):
    def setUp(self):

        # Construct the API provider
        self.ws_provider = SubstrateInterface(    
            url="http://127.0.0.1:9944",
        )

    ### TESTS ###
    def test_accessing_runtime_constants(self):
        ws_provider = self.ws_provider

        # List of available runtime constants in the metadata is well over 10 entries
        constant_list = ws_provider.get_metadata_constants()
        self.assertTrue(len(constant_list) > 10)

        # Retrieve the Existential Deposit constant on Moonbeam, which is 0
        constant = ws_provider.get_constant("Balances", "ExistentialDeposit")
        self.assertTrue(constant == 0)

    def test_retrieving_blocks_and_extrinsics(self):
        ws_provider = self.ws_provider

        # As the node that the tests are run against is a fresh one, we have only the genesis block. 
        # No fun :(

        # Retrieve the latest block
        block = ws_provider.get_block()
        self.assertTrue(block["header"]["number"] == 0)

        # Retrieve the latest finalized block
        block = ws_provider.get_block_header(finalized_only=True)
        self.assertTrue(block["header"]["number"] == 0)

        # Retrieve a block given its Substrate block hash
        block_hash = "0xa083a319f1a9a54113b535c93c4967cf27babe9bd30aa977ade3129d223ff354"
        block = ws_provider.get_block(block_hash=block_hash)
        self.assertTrue(block["header"]["number"] == 0)

        # Iterate through the extrinsics inside the block
        signed_extrinsics = 0
        non_signed_extrinsics = 0
        for extrinsic in block["extrinsics"]:
            if "address" in extrinsic:
                signed_extrinsics = signed_extrinsics + 1
            else:
                non_signed_extrinsics = non_signed_extrinsics + 1
        
        self.assertTrue(signed_extrinsics == 0)
        self.assertTrue(non_signed_extrinsics == 0)

    # def test_subscribing_to_new_block_headers(self):
    # To test a subscription pattern we'll have to mock up the library
    # Therefore, there's no point IMHO
        
    def test_querying_for_storage_information(self):
        ws_provider = self.ws_provider

        # List of available storage functions in the metadata
        method_list = ws_provider.get_metadata_storage_functions()
        self.assertTrue(len(method_list) > 10)

        # Query basic account information
        account_info = ws_provider.query(
            module="System",
            storage_function="Account",
            params=["0x578002f699722394afc52169069a1FfC98DA36f1"],
        )
        self.assertTrue(account_info.value["nonce"] > 0)
        self.assertTrue(account_info.value["data"]["free"] > 0)

        # Query candidate pool information from Moonbeam's Parachain Staking module
        candidate_pool_info = ws_provider.query(
            module="ParachainStaking", storage_function="CandidatePool", params=[]
        )
        # Candidates must have something at stake
        self.assertTrue(candidate_pool_info[0]["amount"] > 1000000000000000000)


    def tearDown(self) -> None:
        return super().tearDown()


if __name__ == "__main__":
    unittest.main()
