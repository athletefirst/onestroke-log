# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "marimo>=0.17.0",
#     "pyzmq>=27.1.0",
# ]
# ///

import marimo

__generated_with = "0.18.4"
app = marimo.App(width="medium")

with app.setup:
    import marimo as mo


@app.cell
def _():
    mo.md(r"""
    # Importing local modules

    [https://docs.marimo.io/guides/package_management/importing_packages/#importing-local-modules](https://docs.marimo.io/guides/package_management/importing_packages/#importing-local-modules)
    """)
    return


@app.cell
def _():
    import hello

    hello.say_hello("marimo")
    return


if __name__ == "__main__":
    app.run()
