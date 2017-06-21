pragma solidity ^0.4.10;
//0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef
//1495117646
contract VertogasRegistrar {
    /* State variables */
    address public admin;
    mapping(bytes32 => certificate) public certifRegistrar;
    uint40 public emittedCertificateCount;
    struct certificate{
        address owner;
        uint timeLimit;
    }
    /* Modifiers */
    modifier isAllowed(bytes32 _certifID) {
        require(msg.sender == certifRegistrar[_certifID].owner &&
        now < certifRegistrar[_certifID].timeLimit);
        _;
    }
    modifier isAdmin() {
        require(msg.sender == admin);
        _;
    }
    /* Events */
    event NewCertificate(bytes32 metaData, bytes32 certifID, address owner);
    event Transfer(bytes32 certifID, address indexed from, address indexed to);
    event Claim(bytes32 certifID, address indexed from);
    event AdminCleaning(bytes32 certifID);
    /* Constructor and destructor and ...*/
    function VertogasRegistrar() {
             admin = msg.sender;
    }
    function destruct() isAdmin {
             selfdestruct(admin);
    }
    function changeAdmin(address _admin) isAdmin {
             admin = _admin;
    }
    /* Methods */
    function newCertificate(bytes32 _metaData, address _owner) isAdmin {
             emittedCertificateCount++;
             bytes32 _certifID = sha3(_metaData, emittedCertificateCount); //certifID are therefore unique
             certifRegistrar[_certifID] = certificate(_owner, now + 1 years);
             NewCertificate(_metaData, _certifID, _owner);
    }
    function transfer(bytes32 _certifID, address _to) isAllowed(_certifID) {
             certifRegistrar[_certifID].owner = _to;
             Transfer(_certifID, msg.sender, _to);
    }
    function getCertificateOwner(bytes32 _certifID) constant returns (address owner) {
             return certifRegistrar[_certifID].owner;
    }
    function getCertificateTimelimit(bytes32 _certifID) constant returns (uint timeLimit) {
             return certifRegistrar[_certifID].timeLimit;
    }
    function claim(bytes32 _certifID) isAllowed(_certifID) {
             delete(certifRegistrar[_certifID]);
             Claim(_certifID, msg.sender);
    }
    function adminCleaning(bytes32 _certifID) isAdmin {
             delete(certifRegistrar[_certifID]);
             AdminCleaning(_certifID);
    }
}