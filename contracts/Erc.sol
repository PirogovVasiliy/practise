// SPDX-License-Identifier: MIT

pragma solidity ^0.8.24;

contract ERC20{
    uint totalTokens;
    address owner;
    mapping(address => uint) balances;
    string _name;
    string _symbol;

    event Transfer(address indexed from, address indexed to, uint amount);

    event Approve(address indexed owner, address indexed to, uint amount);

    function name() external view returns(string memory) {
        return _name;
    }

    function symbol() external view returns(string memory) {
        return _symbol;
    }

    function decimals() external pure returns(uint) { // сколько десятичных знаков после запятой 
        return 18; // 1 token = 1 wei
    }

    function totalSupply() external view returns(uint) { //общее количество токенов
        return totalTokens;
    }

    modifier enoughTokens(address _from, uint _amount) {
        require(balanceOf(_from) >= _amount, "not enough tokens!");
        _;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not an owner!");
        _;
    }

    constructor(string memory name_, string memory symbol_, uint initialSupply, address shop) {
        _name = name_;
        _symbol = symbol_;
        owner = msg.sender;
        mint(initialSupply, shop); 
    }

    function balanceOf(address account) public view returns(uint) {
        return balances[account];
    }

    function transfer(address to, uint amount) external enoughTokens(msg.sender, amount) {
        balances[msg.sender] -= amount;
        balances[to] += amount;
        emit Transfer(msg.sender, to, amount);
    }

    function mint(uint amount, address shop) public onlyOwner { //ввести количество токенов в оборот
        balances[shop] += amount;
        totalTokens += amount;
        emit Transfer(address(0), shop, amount);
    }

    function burn(address _from, uint amount) public onlyOwner { //вывести количесвто токенов
        balances[_from] -= amount;
        totalTokens -= amount;
    }

    function transferFrom(address sender, address recipient, uint amount) public enoughTokens(sender, amount) {
        balances[sender] -= amount;
        balances[recipient] += amount;
        emit Transfer(sender, recipient, amount);
    } 
}

contract MyToken is ERC20 {
    constructor(address shop) ERC20("MYToken", "MT", 200000000000000000000, shop) {}
}

contract MShop {
    ERC20 private token; 
    address payable private owner;
    event Bought(uint _amount, address indexed _buyer);
    event Sold(uint _amount, address indexed _seller);
    event OtherBlockchainTransfer(uint _amount, uint _chainId, address indexed _to);

    constructor() {
        token = new MyToken(address(this)); //развертование стороннего смарт контракта
        owner = payable(msg.sender);
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "not an owner!");
        _;
    }

    function sell(uint _amountToSell) external {
        require(
            _amountToSell > 0 &&
            token.balanceOf(msg.sender) >= _amountToSell,
            "incorrect amount!"
        );

        token.transferFrom(msg.sender, address(this), _amountToSell);

        payable(msg.sender).transfer(_amountToSell);

        emit Sold(_amountToSell, msg.sender);
    }

    function buy() external payable{
        uint tokensToBuy = msg.value; // 1 wei = 1 token 
        require(tokensToBuy > 0, "not enough funds!");

        require(tokenBalance() >= tokensToBuy, "not enough tokens!");

        token.transfer(msg.sender, tokensToBuy);
        emit Bought(tokensToBuy, msg.sender);
    }

    receive() external payable {
        uint tokensToBuy = msg.value; // 1 wei = 1 token 
        require(tokensToBuy > 0, "not enough funds!");

        require(tokenBalance() >= tokensToBuy, "not enough tokens!");

        token.transfer(msg.sender, tokensToBuy);
        emit Bought(tokensToBuy, msg.sender);
    }

    function tokenBalance() private view returns(uint) {
        return token.balanceOf(address(this));
    }

    function myTokenBalance() external view returns(uint){
        return token.balanceOf(address(msg.sender));
    }

    function transferToBlockchain(address to, uint amount, uint chainId) external{
        require(
            amount > 0 &&
            token.balanceOf(msg.sender) >= amount,
            "incorrect amount!"
        );

        token.burn(msg.sender, amount);

        emit OtherBlockchainTransfer(amount, chainId, to);
    }

    function getSymbol() external view returns(string memory){
        return token.symbol();
    }

    function recieveFromBlockchain(address to, uint amount) external{
        token.mint(amount, address(this));

        token.transfer(to, amount);
    }
}