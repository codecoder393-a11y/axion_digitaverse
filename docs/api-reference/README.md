# Axion Digitaverse API Reference

## Overview
This documentation provides comprehensive details about the Axion Digitaverse API endpoints, their usage, and integration guidelines.

## Base URL
- Production: `https://axion-code-1.onrender.com`
- Development: `http://127.0.0.1:5001`

## API Categories
1. [Authentication](./authentication/README.md)
2. [Wallet Operations](./wallet/README.md)
3. [Smart Contracts](./smart-contracts/README.md)
4. [Real Estate](./real-estate/README.md)
5. [Lending](./lending/README.md)
6. [Axion AI](./axion-ai/README.md)
7. [Blockchain](./blockchain/README.md)
8. [IDE & Development](./ide/README.md)
9. [Agent Management](./agents/README.md)
10. [File Storage](./storage/README.md)

## Common Headers
```json
{
  "Content-Type": "application/json",
  "Accept": "application/json"
}
```

## Authentication
All authenticated endpoints require proper credentials. See the [Authentication Guide](./authentication/README.md) for details.

## Error Handling
Standard error responses follow this format:
```json
{
  "error": "Error message description",
  "code": "ERROR_CODE",
  "details": {}
}
```

## Rate Limiting
API requests are limited to ensure fair usage. See [Rate Limiting](./rate-limiting.md) for details.