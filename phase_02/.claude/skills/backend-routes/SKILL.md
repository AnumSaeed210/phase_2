---
name: backend-routes
description: Generate backend routes, handle requests/responses, and connect to databases. Use for building APIs and server-side applications.
---

# Backend Development: Routes & DB

## Instructions

1. **Route creation**

   - Define RESTful endpoints (GET, POST, PUT, DELETE)
   - Organize routes in separate modules
   - Use proper naming conventions (`/users`, `/products`, etc.)

2. **Request handling**

   - Extract parameters, query strings, and request bodies
   - Validate inputs to ensure data integrity
   - Handle authentication and authorization if needed

3. **Response management**

   - Return JSON responses consistently
   - Include HTTP status codes (200, 201, 400, 404, 500)
   - Handle errors gracefully with descriptive messages

4. **Database connection**
   - Initialize DB connection at app startup
   - Use models or ORM for CRUD operations
   - Handle connection errors and retries

## Best Practices

- Keep route handlers small and modular
- Validate all user input to prevent injection attacks
- Use environment variables for DB credentials
- Log requests and errors for debugging
- Follow RESTful API conventions
