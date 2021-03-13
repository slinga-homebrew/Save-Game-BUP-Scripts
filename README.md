# Save Game BUP Scripts
Scripts and documentation for working with Sega Saturn .BUP save game files. It is our hope that this will be the standardized save game format for Sega Saturn utilities such as [SS Save Parser](https://github.com/hitomi2500/ss-save-parser), [Pseudo Saturn Kai](https://ppcenter.webou.net/pskai/), [Save Game Copier](https://github.com/slinga-homebrew/Save-Game-Copier), [Save Game Extractor](https://github.com/slinga-homebrew/Save-Game-Extractor), and any other utilities. 

## .BUP File Format
The .BUP file format is a 64-byte header that is prepended to the front of the Sega Saturn save game data. Note: This is the data as seen by the game via BUP_Read()\BUP_Write() not as seen by looking at raw memory in the backup address. The .BUP header contains among other fields, a magic signature, save game name (this is the name seen in the Saturn BIOS), save game comment (also seen in the Saturn BIOS), and other various metadata fields used by the Saturn. The multibyte length fields are stored in big endian. Immediately following the 64-byte header is the raw Saturn save data. 

**Bup_header.h** contains definitions for the vmem_bup_header_t structure (the BUP header). Bup_header.h also contains implementations for bup_setdate() and bup_getdate() which are functions for converting between the Sega Saturn's date formats. 

To ensure compatiblity with all tools the .BUP file extension **must** be used. 

## Sample .BUP Saves
Sample .BUP files can be obtained from [Save Game Copier](https://github.com/slinga-homebrew/Save-Game-Copier/tree/master/cd/SATSAVES) as well as from [Pseudo Saturn Kai](https://ppcenter.webou.net/pskai/).   

## bup_parse.py
bup_parse.py is a helper script to convert between .BUP and raw save game files. Usage:

### Validate .BUP file
```python3 bup_parse.py --input_bup <save_game.BUP>```

Ex.

```
python3 bup_parse.py --input_bup SEGARALLY_1.BUP 
Validating SEGARALLY_1.BUP
	Save name: SEGARALLY_1
	Comment: GHOSTS    
	Language: Japanese
	Date: 1994-03-20 23:29:00 (0x721a81)
	Data Size: 62464
	Block Size: 249
	MD5: 07e0a5e3a0e7adc7e4816008af427cbd
Valid .BUP file
```

Will validate and display information about the input bup file. 

### Extract Raw Save From .BUP File
```python3 bup_parse.py --input_bup <save_game.BUP> --extract_raw_save```

Will extract the raw save game from the input bup file.

Ex.

```
python3 bup_parse.py --input_bup SEGARALLY_1.BUP --extract_raw_save
Validating SEGARALLY_1.BUP
	Save name: SEGARALLY_1
	Comment: GHOSTS    
	Language: Japanese
	Date: 1994-03-20 23:29:00 (0x721a81)
	Data Size: 62464
	Block Size: 249
	MD5: 07e0a5e3a0e7adc7e4816008af427cbd
Valid .BUP file
Successfully extracted SEGARALLY_1 (62464)
```

### Create .BUP from raw save
```python3 bup_parse.py --save_name <name> --save_comment <comment> --save_date <date> --save_language <language> --input_save <raw_save.bin>```

Given a raw save game, will create a valid .BUP file. All parameters except for input_save and save_name are optional. 

Ex. 
```
python3 bup_parse.py --save_name SEGARALLY_1 --input_save SEGARALLY_1.BIN
Successfully created SEGARALLY_1.BUP from SEGARALLY_1 raw save

python3 bup_parse.py --save_name SEGARALLY_1 --input_save SEGARALLY_1.BIN --save_date 2020-12-12 --save_language English
Successfully created SEGARALLY_1.BUP from SEGARALLY_1 raw save
```

## Credits
* [Cafe-Alpha](https://github.com/cafe-alpha/) is the creator of the .BUP file format
* [Yabause](https://github.com/Yabause/yabause) for bup_getdate() and bup_setdate() functions
* [Jo Engine](https://github.com/johannes-fetz/joengine) for various structure definitions
