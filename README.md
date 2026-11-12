# Easy Download Nerd Fonts

## Use

```bash
$ git clone https://github.com/dopelDev/install_nerd_fonts.git
$ cd install_nerd_fonts
$ python3 -m pip install -r requirements.txt
```

## Use with Make

Create a virtual environment and install dependencies:

```bash
$ make install
```

List available fonts:

```bash
$ make list
```

Inspect matching fonts:

```bash
$ make show INCLUDE=Fira
```

Open the Fire CLI menu:

```bash
$ make menu
```

Open the Textual menu:

```bash
$ make tui
```

Download matching fonts:

```bash
$ make download INCLUDE=Fira DESTINATION=fonts
```

Run tests:

```bash
$ make test
```

Clean local generated files:

```bash
$ make clean
$ make clean-downloads
```

List available fonts:

```bash
$ python3 install_nerd_fonts.py list
```

Show details for a matching font or group:

```bash
$ python3 install_nerd_fonts.py show Fira
```

Open the interactive Fire CLI menu:

```bash
$ python3 install_nerd_fonts.py menu --destination fonts
```

Download a group or matching font name:

```bash
$ python3 install_nerd_fonts.py download Fira --destination fonts
```

Exclude matching fonts from a download:

```bash
$ python3 install_nerd_fonts.py download Mono --exclude Propo --destination fonts
```

Open the Textual menu to choose which fonts to download:

```bash
$ python3 install_nerd_fonts.py tui --destination fonts
```

The Textual menu includes include/exclude filters, an editable destination, a selected-font preview, selection actions, and download status.

Download all fonts:

```bash
$ python3 install_nerd_fonts.py download_all --destination fonts
```

Downloads show a preview first and ask for confirmation. Use `--yes=True` to skip the confirmation in automation.

Unzip downloaded fonts:

```bash
$ ls fonts/*.zip | xargs -I _ sudo unzip _ -d <directory>
```
