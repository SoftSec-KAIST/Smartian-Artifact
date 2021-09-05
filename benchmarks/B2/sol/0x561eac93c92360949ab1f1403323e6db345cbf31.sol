/*
 * @source: etherscan.io 
 * @author: -
 * @vulnerable_at_lines: 54
 */

pragma solidity ^0.4.19;

contract BANK_SAFE
{
    mapping (address=>uint256) public balances;   
   
    uint public MinSum;
    
    bool intitalized;
    
    function SetMinSum(uint _val)
    public
    {
        if(intitalized)throw;
        MinSum = _val;
    }
    
    function SetLogFile(address _log)
    public
    {
        if(intitalized)throw;
    }
    
    function Initialized()
    public
    {
        intitalized = true;
    }
    
    function Deposit()
    public
    payable
    {
        balances[msg.sender]+= msg.value;
    }
    
    function Collect(uint _am)
    public
    payable
    {
        if(balances[msg.sender]>=MinSum && balances[msg.sender]>=_am)
        {
            // <yes> <report> REENTRANCY
            if(msg.sender.call.value(_am)())
            {
                balances[msg.sender]-=_am;
            }
        }
    }
    
    function() 
    public 
    payable
    {
        Deposit();
    }
    
}
