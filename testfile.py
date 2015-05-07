#!/usr/bin/python

import sys, getopt
import string

inputfile = None
outputfile = None
outstream = None
digs = string.digits + string.letters

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
    
def buildGlyphTables(numDicts):
    setlist = []    
    get_bin = lambda x, n: x >= 0 and str(bin(x))[2:].zfill(n) or "-" + str(bin(x))[3:].zfill(n)    
    for y in range(numDicts):
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
    

def writeLine(str):
    if(outputfile == None):
        print(str)
    else:
        outstream.write(str + '\n')
    

def main(argv):
    global inputfile 
    global outputfile
    global outstream
    print('')
    
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
    
    lines = [line.strip() for line in open(inputfile)] 
    valid = False
    comment = None
    numDicts = 7
    missingGlyphs = 0
    
    dictlist = [dict() for x in range(numDicts)]
    glyphTables = buildGlyphTables(numDicts)
    
    
    for line in lines:
        parsedLines = line.split('#')
        content = parsedLines[0].strip()  
        comment = ''.join(parsedLines[1::1])
        try:
            dec = int(content,2)
            drev = str(dec)[::-1]
            brev = int(content[::-1],2)
            l = len(content)-1
            if(content in glyphTables[l]):
                glyph = str(l+1) + '-' + str(glyphTables[l][content]).zfill(2)
            else:
                glyph = ' *'
                missingGlyphs += 1
            
            b12 = int2base(dec, 12)
            
            lidx = len(content)-1;
            
            if(content not in dictlist[lidx]):
                dictlist[lidx][content] = 1
            else:
                #num = dictlist[lidx][content]
                dictlist[lidx][content] += 1
            
            if not(valid):
                writeLine('\t\tDec\trDec\tfDec\tGly\tB12')
                valid = True
        except:
            dec = ''
            drev = ''
            brev = ''
            glyph = ''
            b12 = ''
            valid = False
                
        writeLine("{}\t\t{}\t{}\t{}\t{}\t{}\t{}".format(content, dec, brev, drev, glyph, b12, comment))
    
    writeLine("-----------------------------------------------------------------------\n\nSummary:")
    for n in range(numDicts):
        entries = len(dictlist[n])
        if(entries > 0):
            writeLine("{}-bit glyphs: {} (of {} possible)".format(n+1, entries, len(glyphTables[n])))

    if(missingGlyphs > 0):
        writeLine("MISSING glyphs: {}".format(missingGlyphs))

    writeLine('')

    if(outstream != None):
        outstream.close()
        print("Writing file => \'" + outputfile + "\'\n")

if __name__ == "__main__":
    main(sys.argv[1:])