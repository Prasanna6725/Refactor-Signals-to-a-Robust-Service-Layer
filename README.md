# Signal -> Service Example

This project demonstrates the pitfalls of using Django signals for core business logic and refactors the logic into an explicit service layer. It includes tests and a benchmark management command comparing a signal-style per-object update with an optimized bulk update.

See .env.example for required environment variables, and run `docker-compose up --build` to start the application and the database.

Run tests with `docker-compose run --rm app python manage.py test` (or locally inside a virtualenv).

Run the benchmark command:

```
python manage.py benchmark_updates --count 1000
```
