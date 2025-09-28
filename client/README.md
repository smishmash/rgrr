# RGRr Client

RGRr client provides a web interface to visualize resource distribution simulations from the RGRr
server.

## Project Structure

```
client/
├┬─ src/main/rgrr/client/app.cljs  # Main ClojureScript application code
|└── ...                            # Other ClojureScript source files
├── public/index.html               # Main HTML file for the application
├── shadow-cljs.edn                 # shadow-cljs build configuration
├── package.json                    # Node.js project manifest (dependencies, scripts)
├── package-lock.json               # Node.js dependency lock file
└── README.md                       # Project documentation
```

## Getting Started

### Installation

1. Navigate to the client directory:
```bash
cd client
```

2. Install JavaScript dependencies (including `shadow-cljs` and React):
```bash
npm install
```

### Usage

1. Start the development server. The server will be available at `http://localhost:9630`.
   ```bash
   npx shadow-cljs start
   ```
   This server will be available at When you're done or need to restart the server, do so with:
   ```bash
   npx shadow-cljs stop
   ```

2. Start the rgrr server in the `server` subdirectory of this project.

3. Have the browser watch for client updates. This includes editing ClojureScript or changing
   assets:
   ```bash
   npx shadow-cljs watch client
   ```
   This command will start the client at `http://localhost:8080/`.

### Running Tests

Automated tests for the client are not explicitly configured in the build system at this time.
Client-side functionality can be verified by running the application in a browser.

## License

This project is open source and available under the MIT License. See the main `LICENSE` file in the project root for details.
