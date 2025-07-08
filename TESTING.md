# Testing Guide

## How to Run Tests

- **In the app container:**
  1. Start services:
     ```bash
     docker-compose up --build
     ```
  2. Open a shell in the app container:
     ```bash
     docker-compose exec app bash
     ```
  3. Run tests:
     ```bash
     pytest tests/ -v
     ```

- **Locally:**
  ```bash
  pytest tests/ -v
  ```

## Test Types
- Unit and API tests are all in `tests/`.
- Use markers to filter:
  ```bash
  pytest -m "unit"
  pytest -m "api"
  ```

## CI/CD
- All tests run automatically on GitHub Actions for every push/PR.

---
Keep tests fast, isolated, and meaningful. 