# Client Development Guidelines

## Commands

- Start development server and repl, and set up client watch: `npx shadow-cljs run repl/start`
- Clean build artifacts: `npx shadow-cljs clean`
- Install ClojureScript dependencies: `npm install` (from `client/` directory)

## Key URLs

- Connect to client application at http://localhost:8080/
- Connect to app server at http://localhost:9630/

## Code Style

- Follow Clojure/ClojureScript community conventions.
- Use 2-space indentation.
- Organize imports alphabetically.
- Use clear, descriptive names for functions and variables (kebab-case).
- Prefer pure functions and immutable data structures where appropriate.
- Docstrings should explain the purpose and usage of functions/components.

## Testing

Automated tests for the client are not explicitly configured at this time. Manual testing is
performed by running the application in a browser.
