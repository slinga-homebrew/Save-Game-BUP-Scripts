# Save Game BUP Scripts
Scripts and documentation for working with Sega Saturn .BUP save game files. It is our hope that this will be the standardized save game format for Sega Saturn utilities such as [SS Save Parser](https://github.com/hitomi2500/ss-save-parser), [Pseudo Saturn Kai](https://ppcenter.webou.net/pskai/), [Save Game Copier](https://github.com/slinga-homebrew/Save-Game-Copier), [Save Game Extractor](https://github.com/slinga-homebrew/Save-Game-Extractor), and any other utilities. 

## .BUP File Format
The .BUP file format is a 64-byte header that is prepended to the front of raw Saturn save game files. It contains among other fields, a magic signature, save game name (this is the name seen in the Saturn BIOS), save game comment (also seen in the Saturn BIOS), and other various metadata fields used by the Saturn. The multibyte length fields are stored in big endian. Immediately following the 64-byte header is the raw Saturn save data. 

**Bup_header.h** contains definitions for the vmem_bup_header_t structure (the BUP header). Bup_header.h also contains implementations for bup_setdate() and bup_getdate() which are functions for converting between the Sega Saturn's date formats. 

To ensure compatiblity with all tools the .BUP file extension **must** be used. 

## bup_parse.py
bup_parse.py is a helper script to convert between .BUP and raw save game files. Usage:

### Validate .BUP file
```python3 parse_bup.py --input_bup <save_game.bup>```

Will validate and display information about the input bup file. 

### Extract raw save from .BUP file
```python3 parse_bup.py --input_bup <save_game.bup> --extract_raw_save```

Will extract the raw save game from the input bup file.

### Create .BUP from raw save
```python3 parse_bup.py --save_name <name> --save_comment <comment> --save_date <date> --save_language <language> -input_save <raw_save.bin>```

Given a raw save game, will create a valid .BUP file. All parameters except for input_save and save_name are optional. 

## Credits
* [Cafe-Alpha](https://github.com/cafe-alpha/) is the creator of the .BUP file format
* [Yabause](https://github.com/Yabause/yabause) for bup_getdate() and bup_setdate() functions
* [Jo Engine](https://github.com/johannes-fetz/joengine) for various structure definitions
