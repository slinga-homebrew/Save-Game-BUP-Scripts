# Python script to dump\create Sega Saturn .BUP save game files

import time
import datetime

BUP_HEADER_SIZE = 64
BUP_HEADER_MAGIC = "Vmem"
BUP_EXTENSION = ".BUP" # required file extension

MAX_SAVE_NAME_LENGTH = 12
MAX_SAVE_COMMENT_LENGTH = 11

import sys
import getopt

# prints out script usage and quits
def usage():
    print("\nUsage:")

    print("Validate .BUP file.")
    print('python3 parse_bup.py --input_bup <save_game.bup>\n')

    print("Extract raw save from .BUP file.")
    print('python3 parse_bup.py --input_bup <save_game.bup> --extract_raw_save\n')

    print("Create .BUP from raw save.")
    print('python3 parse_bup.py --save_name <name> --save_comment <comment> --save_date <date> --save_language <language> -input_save <raw_save.bin>\n')

    sys.exit(1)

# returns the language based on the langId
def getBUPLanguage(langId):

    if langId == 0:
        return "Japanese"
    elif langId == 1:
        return "English"
    elif langId == 2:
        return "Francais"
    elif langId == 3:
        return "Deutsch"
    elif langId == 4:
        return "Espanol"
    elif langId == 5:
        return "Italiano"

    # language not found
    return None

# returns the langId based on the language
def getBUPLangId(language):

    language = language.lower()

    if language == "japanese":
        return 0
    if language == "english":
        return 1
    if language == "francais":
        return 2
    if language == "deutsch":
        return 3
    if language == "espanol":
        return 4
    if language == "italiano":
        return 5

    # language not found
    return None

# converts a 4-byte BUP date to a Python datetime
# ported from bup_getdate()
def convertBUPDatetoDatetime(bupDate):

    # minutes
    mins = (bupDate % 60) & 0xFF

    hours = int(bupDate % (60*24) / 60) & 0xFF

    # Compute days count
    div = bupDate / (60*24);
    div = int(div)

    year_base   = int(div / ((365*4) + 1))
    year_base = int(year_base * 4)
    days_remain = int(div % ((365*4) + 1))

    days_count = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    month = 0;

    for i in range(0, 48):
        days_per_month = days_count[i % 12];
        if i == 1:
            days_per_month += 1

        if days_remain < days_per_month:
            break

        days_remain -= days_per_month
        month += 1

        if i % 12 == 11:
            month = 0
            year_base += 1

    year_base += 1980
    month += 1
    days_remain += 1

    return datetime.datetime(year_base, month, days_remain, hours, mins)

# converts a Python datetime to a 4-byte BUP date
# ported from bup_setdate()
def convertDatetimetoBUPDate(dt):

    # Table of elapsed days per month
    monthtbl = [
        31,
        31+28,
        31+28+31,
        31+28+31+30,
        31+28+31+30+31,
        31+28+31+30+31+30,
        31+28+31+30+31+30+31,
        31+28+31+30+31+30+31+31,
        31+28+31+30+31+30+31+31+30,
        31+28+31+30+31+30+31+31+30+31,
        31+28+31+30+31+30+31+31+30+31+30
    ]

    date = 0
    data = 0
    remainder = 0

    # invalid all NULLs case
    if dt.year  == 0 and dt.month == 0 and dt.day and dt.hour == 0 and dt.minutes== 0:
        return 0x008246A0

    # Add year to result
    data = int((dt.year - 1980)) & 0xFF
    date = int(data / 4) * 0x5B5
    date = int(date)

    data = int(data)
    remainder = data % 4

    if remainder:
        date += (remainder * 0x16D) + 1 # 0x16D = 365

    date = int(date)

    # Leap year fix.
    year = dt.year & 0xFFFF
    leap_year = 0
    if (year % 4) != 0:
        leap_year = 0;
    elif (year % 100) != 0:
        leap_year = 1
    elif (year % 400) != 0:
        leap_year = 0
    else:
        leap_year = 1

    date -= 1
    if leap_year != 0 and dt.month == 2:
        date -= 1

    if (year > 2000) and ((year % 100) == 0) and (dt.month == 2):
        date -= 1

    # Add month to result
    data = dt.month
    if data != 1 and data < 13:
        date += monthtbl[data - 2];
        if date > 2 and remainder == 0:
            date += 1

    # Add day to result
    date += dt.day
    date *= 0x5A0

    # Add hour to result
    date += (dt.hour * 0x3C)

    # Add minute to result
    date += dt.minute

    return int(date)

# basic sanity checks of the .BUP file
# exits if error is detected
# file has already been checked for .BUP extension
def validateBUPData(bupData):

    if len(bupData) < BUP_HEADER_SIZE:
        print(len(bupData))
        print("Invalid BUP file: too small (" + str(len(bupData)) + ")")
        sys.exit(-1)

    magic = bupData[0:4].decode("ascii")
    if magic != BUP_HEADER_MAGIC:
        print("Invalid BUP file: incorrect magic bytes (" + magici + ")")
        sys.exit(-1)

    # read fields from the dir struct
    saveName = bupData[16:28].decode("ascii").rstrip('\x00')
    print("\tSave name: " + saveName)

    comment = bupData[28:39].decode("sjis")
    print("\tComment: " + comment)

    langId = int(bupData[39])
    language = getBUPLanguage(langId)

    if langId == None:
        print("Invalid BUP file: incorrect magic bytes")
        sys.exit(-1)
    print("\tLanguage: " + language)

    date = int.from_bytes(bupData[40:44], 'big')
    dataSize = int.from_bytes(bupData[44:48], 'big')
    blockSize = int.from_bytes(bupData[48:50], 'big')

    dt = convertBUPDatetoDatetime(date)
    print("\tDate: " + str(dt) + " (" + hex(date) + ")")

    print("\tData Size: " + str(dataSize))
    print("\tBlock Size: " + str(blockSize))

    if dataSize != len(bupData) - BUP_HEADER_SIZE:
        print("Invalid BUP file: incorrect save size")
        print("Expected " + str(len(bupData) - BUP_HEADER_SIZE));
        print("Got " + str(dataSize))
        sys.exit(-1)

    # .BUP is valid
    return saveName

# on success returns a .BUP file
def createBUPHeader(saveName, saveComment, saveDate, saveLanguage, saveData):

    zero_int = 0

    # create the vmem_bup_header
    bupHeader  = b''

    # magic
    bupHeader += BUP_HEADER_MAGIC.encode('utf-8')

    # save id, unused
    bupHeader += zero_int.to_bytes(4, "big")

    # stats, unused
    bupHeader += zero_int.to_bytes(4, "big")

    # usused1, unused
    bupHeader += zero_int.to_bytes(4, "big")

    #
    # dir struct
    #

    # saveName is 11 characters + NULL terminator
    if len(saveName) > MAX_SAVE_NAME_LENGTH - 1:
        print("Save name must be less than " + str(MAX_SAVE_NAME_LENGTH) + " characters!!")
        sys.exit(-1)

    while len(saveName) < MAX_SAVE_NAME_LENGTH:
        saveName += '\x00'

    bupHeader += saveName.encode('utf-8')

    # saveComment is 10 characters + NULL terminator
    if len(saveComment) > MAX_SAVE_COMMENT_LENGTH - 1:
        print("Comment name must be less than " + str(MAX_SAVE_COMMENT_LENGTH) + " characters!!")
        sys.exit(-1)

    while len(saveComment) < MAX_SAVE_COMMENT_LENGTH:
        saveComment += '\x00'

    bupHeader += saveComment.encode('utf-8')

    # langId is one byte
    langId = getBUPLangId(saveLanguage)

    if langId == None:
        print("Save language must be one of: Japanese, English, Francais, Deutsch, Espanol, or Italiano")
        sys.exit(-1)

    bupHeader += langId.to_bytes(1, "big")

    # four bytes of date
    date = convertDatetimetoBUPDate(saveDate)
    bupHeader += date.to_bytes(4, "big")

    # four bytes of datasize
    saveSize = len(saveData)
    bupHeader += saveSize.to_bytes(4, "big")

    # two bytes of blocksize, we can leave this zero
    bupHeader += langId.to_bytes(2, "big")

    # two bytes of padding
    bupHeader += zero_int.to_bytes(2, "big")

    #
    # end of dir struct
    #

    # 4 byte date structure is repeated
    bupHeader += date.to_bytes(4, "big")

    # 8 bytes more of unsused2 padding
    bupHeader += date.to_bytes(8, "big")

    if len(bupHeader) != BUP_HEADER_SIZE:
        print("Invalid bupHeader length!!")
        sys.exit(-1)

    # concatenate the bupHeader with the saveData
    bupHeader = bupHeader + saveData

    return bupHeader

def main(argv):

    inSaveFilename = ""
    outSaveFilename = ""
    inSaveBuf = b''
    outSaveBuf = b''
    extractSave = False

    inBUPFilename = ""
    inBUPBuf = b''

    # default .BUP header values
    saveName = ""
    saveComment = "SGC"
    saveDate = datetime.datetime(1994, 11, 24) # launch date of the Saturn
    saveLanguage = "English"

    try:
        opts, args = getopt.getopt(argv,"h",["help", "input_bup=", "extract_raw_save", "save_name=", "save_comment=", "save_date=", "save_language=", "input_save="])
    except getopt.GetoptError:
        usage()

    for opt, arg in opts:
        if opt in ('-h', "--help"):
            usage()
            sys.exit()
        elif opt in ("-i", "--input_bup"):
            inBUPFilename = arg
        elif opt in ("--extract_raw_save"):
            extractSave = True
        elif opt in ("--save_name"):
            saveName = arg
        elif opt in ("--save_comment"):
            saveComment = arg
        elif opt in ("--save_date"):
            dateStr = arg

            try:
                t = time.strptime(dateStr, '%Y-%m-%d')
                saveDate = datetime.datetime(*t[:6])
            except ValueError:
                print(dateStr + ' is not a proper date string. Must be YYYY-MM-D')
                sys.exit(-1)

        elif opt in ("--save_language"):
            saveLanguage = arg
        elif opt in ("--input_save"):
            inSaveFilename = arg

    if len(inSaveFilename) == 0 and len(inBUPFilename) == 0:
        print("Input .BUP or input .BUP file must be supplied.")
        usage()

    if len(inSaveFilename) != 0 and len(inBUPFilename) != 0:
        print("Only one input .BUP or input save file must be supplied.")
        usage()

    if len(inSaveFilename) != 0 and len(saveName) == 0:
        print("save_name is required!!")
        usage()

    # reading from a .BUP file
    if len(inBUPFilename):

        if inBUPFilename.endswith(BUP_EXTENSION) != True:
            print("BUP file must end with .BUP extension.")
            usage()

        # open and sanity check the input save file
        inFile = open(inBUPFilename, "rb")
        inBUPBuf = inFile.read()
        inFile.close()

        print("Validating " + inBUPFilename)
        saveName = validateBUPData(inBUPBuf)
        print("Valid .BUP file")

        if extractSave:
            # everything have the BUP header is the raw save
            outBuf = inBUPBuf[BUP_HEADER_SIZE:]

            outFile = open(saveName, "wb")
            outFile.write(outBuf)
            outFile.close()

            print("Successfully extracted " + saveName + " (" + str(len(outBuf)) + ")")
            return

        return

    # creating a .BUP file
    if len(inSaveFilename):

        # read the save save file
        inFile = open(inSaveFilename, "rb")
        inSaveBuf = inFile.read()
        inFile.close()

        outBUPBuf = createBUPHeader(saveName, saveComment, saveDate, saveLanguage, inSaveBuf)

        # .BUP is the required extension
        outBUPFilename = saveName + BUP_EXTENSION

        outFile = open(outBUPFilename, "wb")
        outFile.write(outBUPBuf)
        outFile.close()

        print("Successfully created " + outBUPFilename + " from " + saveName + " raw save")
        return

if __name__ == "__main__":

    # Python3 only
    if sys.version_info.major < 3:
        print("Python 3 required")
        sys.exit(-1)

    main(sys.argv[1:])
