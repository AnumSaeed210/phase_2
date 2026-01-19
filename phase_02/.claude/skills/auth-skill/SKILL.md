---
name: auth-skill
description: Implement secure authentication flows with signup, signin, password hashing, JWT tokens, and Better Auth integration.
---

# Authentication Skill

## Instructions

1. **User Authentication Flow**

   - Signup: Collect username/email and password
   - Signin: Validate credentials
   - Password hashing: Use strong hashing algorithms (bcrypt, Argon2)
   - JWT tokens: Issue access tokens on successful login
   - Better Auth integration: Optional integration for advanced auth features (e.g., social login, MFA)

2. **Security Measures**

   - Salt passwords before hashing
   - Set JWT expiration and refresh tokens
   - Use HTTPS for API endpoints
   - Validate inputs to prevent injection attacks

3. **Implementation Tips**
   - Use environment variables for secrets
   - Store tokens securely (HTTP-only cookies or secure storage)
   - Keep auth logic modular for reuse
   - Log auth events for monitoring (without logging passwords)

## Best Practices

- Never store plain text passwords
- Keep JWT secret keys safe
- Use minimal scopes/permissions for tokens
- Follow principle of least privilege for user roles
- Ensure endpoints are rate-limited to prevent brute-force attacks
