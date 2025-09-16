# Attack Scenarios Backend API

This is a simple Express.js backend API for managing attack scenarios with MongoDB integration.

## Features

- Create, read, update, and delete attack scenarios
- Mark scenarios as completed/incomplete
- Filter scenarios by completion status
- MongoDB integration with Mongoose
- RESTful API endpoints
- Error handling and validation

## Installation

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables:
   - The `.env` file is already configured with your MongoDB connection string
   - Modify `PORT` if needed (default: 5000)

4. Start the server:
   ```bash
   # Development mode with nodemon
   npm run dev

   # Production mode
   npm start
   ```

## API Endpoints

### Base URL: `http://localhost:5000/api`

#### Health Check
- `GET /api/health` - Check if the server is running

#### Scenarios
- `GET /api/scenarios` - Get all scenarios
- `GET /api/scenarios/:id` - Get a specific scenario by ID
- `POST /api/scenarios` - Create a new scenario
- `PUT /api/scenarios/:id` - Update a scenario
- `DELETE /api/scenarios/:id` - Delete a scenario
- `PUT /api/scenarios/:id/complete` - Mark scenario as completed
- `PUT /api/scenarios/:id/incomplete` - Mark scenario as incomplete
- `GET /api/scenarios/status/completed` - Get all completed scenarios
- `GET /api/scenarios/status/incomplete` - Get all incomplete scenarios

## Request/Response Examples

### Create a Scenario
```json
POST /api/scenarios
{
  "scenarioId": "SC001",
  "title": "Initial Access via Spearphishing",
  "description": "Simulate a spearphishing attack to gain initial access",
  "attackTechniques": [
    {
      "techniqueId": "T1566.001",
      "techniqueName": "Spearphishing Attachment",
      "tactic": "Initial Access"
    }
  ]
}
```

### Mark Scenario as Complete
```json
PUT /api/scenarios/SC001/complete
```

Response:
```json
{
  "success": true,
  "message": "Scenario marked as completed",
  "data": {
    "scenarioId": "SC001",
    "title": "Initial Access via Spearphishing",
    "completed": true,
    "completedAt": "2025-09-16T10:30:00.000Z"
  }
}
```

## Data Schema

### Scenario Model
```javascript
{
  scenarioId: String (required, unique),
  title: String (required),
  description: String,
  attackTechniques: [{
    techniqueId: String,
    techniqueName: String,
    tactic: String
  }],
  completed: Boolean (default: false),
  completedAt: Date,
  createdAt: Date,
  updatedAt: Date
}
```

## Environment Variables

- `MONGODB_URI` - MongoDB connection string
- `PORT` - Server port (default: 5000)
- `NODE_ENV` - Environment mode (development/production)
