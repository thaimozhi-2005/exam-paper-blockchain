/**
 * Truffle configuration for Ganache local blockchain
 * Network: Ganache (localhost:8545)
 * Chain ID: 1337
 */

module.exports = {
    networks: {
        development: {
            host: "127.0.0.1",     // Localhost (Ganache)
            port: 8545,            // Standard Ganache port
            network_id: "*",       // Match any network id
            gas: 6721975,          // Gas limit
            gasPrice: 20000000000  // 20 gwei
        }
    },

    // Configure your compilers
    compilers: {
        solc: {
            version: "0.8.19",    // Fetch exact version from solc-bin
            settings: {
                optimizer: {
                    enabled: true,
                    runs: 200
                }
            }
        }
    },

    // Directory configuration
    contracts_directory: './contracts',
    contracts_build_directory: './build/contracts',
    migrations_directory: './migrations'
};
