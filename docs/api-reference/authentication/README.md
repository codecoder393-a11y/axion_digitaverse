# Authentication API

## Endpoints

### POST /api/login
Login with user credentials.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "token": "string",
  "user": {
    "id": "string",
    "username": "string",
    "role": "string"
  }
}
```

### POST /api/create-user
Register a new user.

**Request:**
```json
{
  "username": "string",
  "password": "string",
  "email": "string",
  "role": "string"
}
```