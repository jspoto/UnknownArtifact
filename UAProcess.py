#!/usr/bin/python

import sys, getopt
import string


def getDigitsForVersion():
    version = sys.version_info
    if(version[0] == 2):
        return string.digits + string.letters
    else:
        return string.digits + string.ascii_letters

        
def levenshtein(s, t):
        ''' From Wikipedia article; Iterative with two matrix rows. '''
        if s == t: return 0
        elif len(s) == 0: return len(t)
        elif len(t) == 0: return len(s)
        v0 = [None] * (len(t) + 1)
        v1 = [None] * (len(t) + 1)
        for i in range(len(v0)):
            v0[i] = i
        for i in range(len(s)):
            v1[0] = i + 1
            for j in range(len(t)):
                cost = 0 if s[i] == t[j] else 1
                v1[j + 1] = min(v1[j] + 1, v0[j + 1] + 1, v0[j] + cost)
            for j in range(len(v0)):
                v0[j] = v1[j]
 
        return v1[len(t)]

        
def int2base(x, base):
    if x < 0: sign = -1
    elif x == 0: return digs[0]
    else: sign = 1
    x *= sign
    digits = []
    while x:
        digits.append(digs[x % base])
        x /= base
    if sign < 0:
        digits.append('-')
    digits.reverse()
    return ''.join(digits)

    
def printUsage():
    print ('test.py -i <inputfile> [-o <outputfile>]')
    return;
    
    
def buildGlyphTables(maxNumBits):
    setlist = []    
    get_bin = lambda x, n: x >= 0 and str(bin(x))[2:].zfill(n) or "-" + str(bin(x))[3:].zfill(n)    
    for y in range(maxNumBits):
        newdict = dict()
        length = y+1
        maxval = 2**length
        glyphID = 0   
        for i in range(maxval):
            bi = get_bin(i,length)  
            broken = False
            count = 0
            for n in range(len(bi)-1):
                if(bi[n] == bi[n+1]):
                    count += 1
                    if(count == 2):
                        broken = True
                        break
                else:
                    count = 0
                
            if not (broken):
                newdict[bi] = glyphID
                glyphID += 1
                
        setlist.append(newdict) 
    return setlist
    
def writeWordList(list, name, tables):
    for n in range(len(list)):
        entries = len(list[n])
        if(entries > 0):
            writeLine("\n  {} Counts ({}-bit)\n  -------------------------".format(name, n+1))
            keylist = list[n].keys()
            keylist.sort()
            for m in keylist:
                if m in tables[n]:
                    gs = glyphString(m, tables)
                else:
                    gs = '****'
                writeLine("  ( {} )\t{}\t{}".format(m, gs, list[n][m])) 
    

def writeLine(str):
    if(outputfile == None):
        print(str)
    else:
        outstream.write(str + '\n')

def glyphString(binStr, tables):
    l = len(binStr)
    idx = l - 1
    glyph = str(l) + '-' + str(tables[idx][binStr]).zfill(2)    
    return glyph
        
inputfile = None
outputfile = None
outstream = None        
digs = getDigitsForVersion()   

def main(argv):
    global inputfile 
    global outputfile
    global outstream
    
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        printUsage()
        sys.exit(2)

    for opt, arg in opts:
        if opt == '-h':
            print ('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    
    if(inputfile == None):
        printUsage()
        sys.exit(2)
        
    if(outputfile != None):
        try:
            outstream = open(outputfile, 'w')
        except:
            print("Unable to open output file \'" + outputfile + "\'")
            sys.exit()

    print('')
    
    totalWords = 0
    totalBits = 0
    
    lines = [line.strip() for line in open(inputfile)] 
    valid = False
    comment = None
    maxNumBits = 7
    missingGlyphs = 0
    lastContent = None
    
    wordList = [dict() for x in range(maxNumBits)]
    glyphList = [dict() for x in range(maxNumBits)]
    glyphTables = buildGlyphTables(maxNumBits)    
    
    for line in lines:
        parsedLines = line.split('#')
        content = parsedLines[0].strip()  
        comment = ''.join(parsedLines[1::1])
        try:
            dec = int(content,2)
            drev = str(dec)[::-1]
            brev = int(content[::-1],2)
            bits = len(content)
            lIdx = bits - 1
            
            if(content in glyphTables[lIdx]):
                glyph = glyphString(content, glyphTables)
                list = glyphList
            else:
                glyph = ' *'
                missingGlyphs += 1
                list = wordList
            
            b12 = int2base(dec, 12)
            
            if(lastContent != None):
                hd = levenshtein(content, lastContent)
            else:
                hd = '-'
            
            # Mark as successfuly parsed entry
            lastContent = content
            totalWords += 1
            totalBits += bits
            
            
            if(content not in list[lIdx]):
                list[lIdx][content] = 1
            else:
                list[lIdx][content] += 1
            
            if not(valid):
                writeLine('\t\tDec\trDec\tfDec\tGlph\tb12\tLev\t|')
                valid = True
        except:
            dec = ''
            drev = ''
            brev = ''
            glyph = ''
            b12 = ''
            hd = ''
            valid = False
            lastContent = None
                
        writeLine("{}\t\t{}\t{}\t{}\t{}\t{}\t{}\t| {}".format(content, dec, brev, drev, glyph, b12, hd, comment))
    
    writeLine("------------------------------------------------------------\n\nProcessing Complete, Summary:\n")

    for n in range(maxNumBits):
        entries = len(glyphList[n])
        if(entries > 0):
            writeLine("  {}-bit glyphs: {} (of {} possible)".format(n+1, entries, len(glyphTables[n])))

    if(missingGlyphs > 0):
        writeLine("  NON-GLYPHS: {}".format(missingGlyphs))
	
    writeLine("\n  Total Words: {0}".format(totalWords))
    writeLine("  Total Bits: {0}".format(totalBits))

#    for n in range(maxNumBits):
#        entries = len(glyphList[n])
#        if(entries > 0):
#            writeLine("\n  Glyph Counts ({}-bit)\n  -------------------------".format(n+1))
#            keylist = glyphList[n].keys()
#            keylist.sort()
#            for m in keylist:
#                if m in glyphTables[n]:
#                    gs = glyphString(m, glyphTables)
#                else:
#                    gs = '****'
#                writeLine("  ( {} )\t{}\t{}".format(m, gs, glyphList[n][m]))

    writeWordList(glyphList, 'Glyph', glyphTables)
    writeWordList(wordList, 'Word (non-glyph)', glyphTables)
             
    writeLine('')

    if(outstream != None):
        outstream.close()
        print("Writing file => \'" + outputfile + "\'\n")

if __name__ == "__main__":
    main(sys.argv[1:])
    