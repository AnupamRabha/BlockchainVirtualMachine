

contract MyContract {
    uint256 public foo;
    uint256 public bar;

    function calc() public {
        foo = 100 + 30;
        bar = foo; 
        foo = 20 - 10;
    }
}