# gnucash-portfolio

A collection of tools for managing an investment portfolio in GnuCash

User-oriented documentation is at http://portfolio.alensiljak.tk

## Introduction

The purpose of the project is to provide tools that help in managing an investment portfolio in a GnuCash book.
The code is written in Python on the server-side, and HTML/JavaScript/CSS on the client-side.

## Development

My development environment in on Windows and consists of the following:

- Visual Studio Code with
  - Python extension
  - ctags (see [new project](https://github.com/universal-ctags/ctags-win32/releases))
- Python 3.6
- node + npm

All the libraries are listed in `requirements.txt` for Python and `package.json` for node.

## Compiling (pre-run)

To install the required development and runtime dependencies, run

```
pip install -r requirements.txt
npm install
```

in the root and app directory since requirements.txt is in the project root and npm's package.json is in the app directory.

Besides this, `piecash`, and `gnucash_portfolio` Python packages must be installed. These are not enabled in the requirements.txt because I'm using the latest development versions cloned directly from GitHub and/or modified locally. If you are happy with the default package, add piecash to requirements.txt or install with pip separately.
The local/development versions of these two libraries can be registered with

`pip install -e <path to>/piecash`

and

`pip install -e .`

for gnucash_portfolio package.

To compile all client-side (.scss, .js) code, run

`npm run build`

in the "app" directory. This will compile production-ready images, styles, and scripts into `/static` folder.

`npm run dev` will do the same but for development. Meaning, the source code will not be minimized and webpack will continue monitoring the folders for any changes to the source files.

### CSS

Custom SCSS is compiled with Webpack (`npm run build` or `npm run dev`).

Vendor CSS is bundled with Flask Assets automatically when the site starts.

### JS

Custom JavaScript code is compiled through Webpack.

Vendor libraries are currently bundled through Flask Assets. It collects the vendor code from installed development node modules. Make sure all the npm dependencies are installed in order for this to work.
The bundle will be built automatically during the app runtime. No additional actions required by the user.

## Running

### First-Time Setup

- Config:
  In order to run the app, copy `config/settings.json.template` into `config/settings.json`. The options can be customized via the Settings link in the web app.

### Execution

All the functionality is provided through a web UI. To run, simply run the app with Python. Running

`py app`

from the root folder will do.

There are several ways to run the web app:

1. Run `py app` directly,
2. Run the "run" task from VS Code,
3. Run "run.py run" (This script was created so that the app could be debugged with Python extension for Visual Studio Code).

## Testing

See `tests` directory and documentation and tests there.
Simply run 

`pytest`

to run all tests.

### Lint

pylint can be used to check for errors. You can check the code by doing the following:

- run `utils\lint_app.cmd` from project root directory,
- run lint tasks from vscode,
- run `pylint app/` to run lint on the web app,
- run `pylint gnucash_portfolio` to check the library.

Pay attention to the Error and Fatal lines. See utils/lint_app.cmd script for coloring output.

Ref: [PyLint Output](https://docs.pylint.org/en/1.6.0/output.html)

# Web Application

This project contains the web application implemented in Flask. It is intended to be used as the full GUI for accepting user input (parameters) and displaying the output.

The app is located in the `/app` directory.

It is intended to run on a desktop workstation, with direct access to the GnuCash book file, stored as an SQLite database.

## Benefits

Considering several factors below, it might be preferrable to use an independent application to work with Portfolio then to provide the UI functionality through GnuCash reports using gnucash_utilities project. This approach would utilize the gnucash book/database directly.

- Ease of development  
Developing reports on piecash stack seems fairly straightforward and much simpler than Scheme, GnuCash reporting engine. The control of the output is also easier by directly editing HTML templates and CSS styles.

- Performance  
Comparing the output through GnuCash reports on Windows to the output produced using the Python stack (flask + jinja HTML output + piecash), the advantage is significantly on the side of the Python components.

# Reports

An approach using gnucash_utilities project is found in the /reports directory.

The basic idea here is to have GnuCash open a custom report, which runs a Python script, which generates an HTML output.
Gnucash_utilities project provides utilities that generate the Scheme links in the user profile directory. You need to create the Python scripts, which return the HTML output generated with Jinja templates (or any other).

This approach has been abandoned due to the performance benefit of using the web app directly for all data input and output.
