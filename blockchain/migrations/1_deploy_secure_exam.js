/**
 * Migration script for deploying SecureExamPaper contract
 */

const SecureExamPaper = artifacts.require("SecureExamPaper");

module.exports = function (deployer) {
    // Deploy the SecureExamPaper contract
    deployer.deploy(SecureExamPaper).then(() => {
        console.log("✅ SecureExamPaper contract deployed successfully!");
        console.log("📍 Contract Address:", SecureExamPaper.address);
        console.log("\n⚠️  IMPORTANT: Copy this address to backend/config/blockchain.json");
    });
};
