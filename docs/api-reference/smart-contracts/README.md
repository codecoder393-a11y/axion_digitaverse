# Smart Contracts API

## Endpoints

### POST /api/contract/deploy
Deploy a new smart contract.

**Request:**
```json
{
  "contractType": "string",
  "parameters": {
    "key": "value"
  }
}
```

### POST /api/contract/call
Call a deployed smart contract method.

**Request:**
```json
{
  "contractAddress": "string",
  "method": "string",
  "parameters": {
    "key": "value"
  }
}
```

## Contract Types
- Real Estate Contract
- Lending Contract
- Equipment Leasing Contract
- Tender Contract