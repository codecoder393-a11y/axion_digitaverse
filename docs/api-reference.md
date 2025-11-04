# API Reference

## Backend API Endpoints

### Blockchain Operations

#### GET /api/miners
Get list of available miners in the network.

**Response**
```json
{
    "miners": [
        "miner_address_1",
        "miner_address_2"
    ]
}
```

#### POST /api/contract/deploy
Deploy a smart contract to the blockchain.

**Request**
```json
{
    "code": "string",
    "args": [],
    "deployer": "address",
    "miner": "miner_address"
}
```

**Response**
```json
{
    "contract_address": "string",
    "transaction_hash": "string"
}
```

#### POST /api/contract/call
Call a method on a deployed contract.

**Request**
```json
{
    "address": "contract_address",
    "method": "method_name",
    "args": [],
    "caller": "caller_address",
    "miner": "miner_address"
}
```

**Response**
```json
{
    "result": {},
    "transaction_hash": "string"
}
```

### IDE Operations

#### GET /api/ide/list
List files in the IDE workspace.

**Response**
```json
[
    {
        "type": "file|folder",
        "name": "string",
        "children": []
    }
]
```

#### POST /api/ide/open
Open a file in the IDE.

**Request**
```json
{
    "path": "file_path"
}
```

**Response**
```json
{
    "content": "string"
}
```

#### POST /api/ide/save
Save a file in the IDE.

**Request**
```json
{
    "path": "file_path",
    "content": "string"
}
```

**Response**
```json
{
    "success": true
}
```

#### POST /api/ide/run
Run a Python file in the IDE.

**Request**
```json
{
    "path": "file_path"
}
```

**Response**
```json
{
    "output": "string"
}
```

### Smart Contract Development Kit API

#### Class: ContractDevelopmentKit

##### test_contract()
Test a smart contract implementation.

```python
def test_contract(self, contract_class, test_params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parameters:
        contract_class: The contract class to test
        test_params: Dictionary containing test parameters
    
    Returns:
        Dictionary containing test results
    """
```

##### validate_contract()
Validate a smart contract's structure.

```python
def validate_contract(self, contract_class) -> Dict[str, Any]:
    """
    Parameters:
        contract_class: The contract class to validate
    
    Returns:
        Dictionary containing validation results
    """
```

### Smart Contract Base API

#### Class: SmartContract

##### update_state()
Update contract state.

```python
def update_state(self, key: str, value: Any) -> None:
    """
    Parameters:
        key: State variable name
        value: New value
    """
```

##### emit_event()
Emit a contract event.

```python
def _emit_event(self, event_type: str, data: Dict[str, Any]) -> None:
    """
    Parameters:
        event_type: Type of event
        data: Event data
    """
```

### Axion Protocol API

#### Class: AxionProtocol

##### encrypt_sensitive_data()
Encrypt sensitive contract data.

```python
def encrypt_sensitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parameters:
        data: Data to encrypt
    
    Returns:
        Dictionary containing encrypted data and reference
    """
```

##### verify_data_integrity()
Verify data integrity.

```python
def verify_data_integrity(self, data: str, reference_hash: str) -> bool:
    """
    Parameters:
        data: Data to verify
        reference_hash: Hash to verify against
    
    Returns:
        Boolean indicating if data is valid
    """
```

## Frontend Components

### PythonIDE Component

Props and State:
```typescript
interface State {
    tree: FileTreeItem[];
    selected: string;
    content: string;
    output: string;
    miners: string[];
    constructorArgs: string;
    callAddress: string;
    callMethod: string;
    callArgs: string;
}
```

### Contract Interaction Components

#### ContractDeployment
```typescript
interface Props {
    code: string;
    onDeploy: (address: string) => void;
}
```

#### ContractCall
```typescript
interface Props {
    address: string;
    onCall: (result: any) => void;
}
```

## WebSocket Events

### Contract Events
```typescript
interface ContractEvent {
    type: string;
    contract: string;
    data: any;
    timestamp: number;
}
```

### IDE Events
```typescript
interface IDEEvent {
    type: 'save' | 'run' | 'output';
    data: any;
}
```

## Error Codes

### Contract Errors
- `CONTRACT_NOT_FOUND`: Contract address not found
- `METHOD_NOT_FOUND`: Contract method not found
- `INVALID_ARGS`: Invalid method arguments
- `EXECUTION_ERROR`: Contract execution error

### IDE Errors
- `FILE_NOT_FOUND`: File not found in workspace
- `SAVE_ERROR`: Error saving file
- `RUN_ERROR`: Error running Python file
- `SYNTAX_ERROR`: Python syntax error

### Blockchain Errors
- `MINER_NOT_FOUND`: Miner node not found
- `DEPLOY_ERROR`: Contract deployment error
- `TRANSACTION_ERROR`: Transaction execution error

## Response Formats

### Success Response
```json
{
    "success": true,
    "data": {},
    "timestamp": "ISO8601_timestamp"
}
```

### Error Response
```json
{
    "success": false,
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description"
    },
    "timestamp": "ISO8601_timestamp"
}