import { ethers } from "hardhat";

async function main() {
  const contract = await ethers.deployContract("MShop", [], {});
  contract.waitForDeployment()

  console.log(`Deployed contract to: ${await contract.getAddress()}`)
}

//    const Lock = await hre.ethers.getContractFactory("Lock");
//    const lock = await Lock.attach("0x5fbdb2315678afecb367f032d93f642f64180aa3");


main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});