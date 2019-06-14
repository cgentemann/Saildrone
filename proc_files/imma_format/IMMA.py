# -*- coding: utf-8 -*-
# Purpose: Python module for handling IMMA1 data
# Information: IMMA1 documentation is at https://rda.ucar.edu/datasets/ds548.0/#!docs
# History:
# 	Orignated from Philip Brohan python code to read IMMA data, see https://github.com/oldweather/IMMA/blob/master/Python/IMMA/icoads.py
# 	Updated/modified by Zhankun Wang in Oct 2016 to read the IMMA1 format data 

import re     #  Regular Expressions

class IMMA:
   
    def __init__(self):          # Standard instance object
        self.attachments = []    # List of attachments in this instance
        self.data = {}           # Dictionary to hold the parameter values

# Getter and setter for instance parameters
    def __getitem__(self, key): return self.data[key]
    def __setitem__(self, key, item): self.data[key] = item

 # Read in a record from a file
    def read(self,fh):
        line = fh.readline();
        if(line == ""): return   # EOF
        line=line.rstrip("\n")       # Remove trailing newline
    # Core is always present (and first)
        Attachment = 0;
        Length     = 108;

    # Decode each attachment
        while ( len(line) > 0 ):

            # Pad the string with blanks if it's too short
            if ( Length != None and Length > 0 and len(line) < Length ):
                sfmt = "%%%ds" % (Length-len(line))
                line += sfmt % " "
            self.decode(
                line,
                getAttachment(Attachment),
                getParameters(Attachment),
                getDefinitions(Attachment)
            )
            self.attachments.append(int(Attachment))
            if ( Length==None or Length == 0 ):
                break
            line = line[Length:len(line)]
            if ( len(line) > 0 ):
                Attachment = int(line[0:2])
                Length     = line[2:4]
                #print Attachment
                if( re.search("\S",Length)==None): 
                    Length = None
                if ( Length != None ):
                try: 
            Length = int(Length)
                except:
            Length = decode_base36_m(Length)
                    if ( Length != 0 ):
                        Length = int(Length)-4
                        line = line[4:len(line)]
                if(getAttachment(Attachment)==None ):
                    raise("Bad IMMA string","Unsupported attachment ID "+Attachment)

        return 1

# Write out a record to a file
    def write(self,fh):           # fh is a filehandle
        Result = ""
        for Attachment in self.attachments:
            Result += self.encode(
                Attachment,
                getParameters(Attachment),
                getDefinitions(Attachment)
            )
        Result=Result.rstrip()
        fh.write( Result+"\n" )
        return 1

# Extract the parameter values from the string representation
#  of an attachment
    def decode(self,
               as_string,      # String representation of the attachment
               attachment,     # Attachment name
               parameters,     # Attachment parameter array
               definitions):   # Attachment definitions hash
        if( as_string== None ):
            raise("Bad IMMA string","No data to decode")

        Position = 0;
        for i in range(len(parameters)):
            if ( definitions[parameters[i]][0] != None ):
                self[parameters[i]] = as_string[Position:Position+definitions[parameters[i]][0]]
                Position += definitions[parameters[i]][0]
            else:                  # Undefined length - so slurp all the data
                self[parameters[i]] = as_string[Position:len(as_string)]
                self[parameters[i]] = self[parameters[i]].rstrip("\n")
                Position = len(as_string)

        # Blanks mean value is undefined
            if( re.search("\S",self[parameters[i]]) == None ):
                self[parameters[i]] = None
                continue    #  Next parameter

            if ( definitions[parameters[i]][6] == 2 ):  
                self[parameters[i]] = decode_base36(self[parameters[i]])
            if ( definitions[parameters[i]][6] == 1 ):
                self[parameters[i]] = int(self[parameters[i]])
                
            if ( definitions[parameters[i]][5] != None and
                 definitions[parameters[i]][5] != 1.0 ):
                self[parameters[i]] = int(self[parameters[i]])*definitions[parameters[i]][5];


# Make a string representation of an attachment
    def encode (self,
                attachment,    # Attachment number
                parameters,    # Ref to attachment parameter array
                definitions):  # Ref to attachment definitions hash
        Result = ""
        for i in range(len(parameters)):
            if ( self[parameters[i]] != None):
                Tmp = self[parameters[i]]

                # Scale to integer units for output
                if ( definitions[parameters[i]][5] != None ):
                    Tmp /= definitions[parameters[i]][5];
                    Tmp = int(Tmp+0.5)  # nint

                # Encode as base36 if required
                if ( definitions[parameters[i]][6] == 2 ):
                    Tmp = encode_base36(Tmp);

                # Print as an string of the correct length
                if ( definitions[parameters[i]][6] == 1 ):  # Integer

                    if ( definitions[parameters[i]][0] != None ):
                        Lstring = "%%%dd" % (definitions[parameters[i]][0])
                        Tmp = Lstring % (Tmp)
                    else:
                        # Undefined length - don't try to constrain it
                        Tmp = "%d" % (Tmp)

                else:                                      # String

                    if ( definitions[parameters[i]][0] != None ):
                        Lstring = "%%-%ds" % (definitions[parameters[i]][0])
                        Tmp = Lstring % (Tmp)
                    else:
                        Tmp = "%-s" % (Tmp)

                Result += Tmp

            else:  # Undefined data - make a blank string of the corect length

                if ( definitions[parameters[i]][0] != None ):
                    Lstring = "%%%ds" % (definitions[parameters[i]][0])
                    Result += Lstring % (" ")

                else: # Undefined data with unknown length - should never happen
                    Result += " ";

    # Done all the parameters, add the ID and length to the start
    # (except for core)
        if ( attachment != 0 ):
            if ( attachment != 99 ):
                Result = "%2d%2d%s" % (attachment, len(Result) + 4, Result)
            else:
                Result = "%2d 0%s" % (attachment, Result)

        return Result

# Functions in the IMMA namespace, but outside the class

# Create a record and read it in from a file
def read(fh):           # fh is a filehandle 
    imma_local = IMMA()
    imma_local.read(fh)
    return imma_local

def getAttachment(i):
    return attachment["%02d" % i]
def getParameters(i):
    return parameters["%02d" % i]
def getDefinitions(i):
    return definitions["%02d" % i]

# Convert a multi-digit base36 value to base 10
def decode_base36_m(t):
    xx = list(t)
    xx.reverse()
    dig10 = 0
    for i,x in enumerate(xx):
	dig10+=36**i*decode_base36(x)
    return dig10
    

# Convert a single-digit base36 value to base 10
def decode_base36(t): 
    return '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'.find(t)

# Convert a base 10 value in the range 0-35 to base36
def encode_base36(t):
    return '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'[t:t+1]


###
### Data for each attachment type
###

attachment  = {}  # Dictionaries, so indexed by %02d string
parameters  = {}
definitions = {}

#
# CORE
#

attachment['00'] = 'CORE'

# List of parameters in CORE section
# In the order they are in on disc
parameters['00'] = ('YR','MO','DY','HR','LAT','LON','IM','ATTC','TI','LI','DS','VS','NID','II','ID','C1','DI','D','WI','W','VI','VV','WW','W1','SLP','A','PPP','IT','AT','WBTI','WBT','DPTI','DPT','SI','SST','N','NH','CL','HI','H','CM','CH','WD','WP','WH','SD','SP','SH')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['00'] = {
       'YR' : (   4, 1600.   , 2024.   ,     None,     None, 1.      , 1), # 1
       'MO' : (   2,    1.   ,   12.   ,     None,     None, 1.      , 1), # 2
       'DY' : (   2,    1.   ,   31.   ,     None,     None, 1.      , 1), # 3
       'HR' : (   4,    0.00 ,   23.99 ,     None,     None, 0.01    , 1), # 4
      'LAT' : (   5,  -90.00 ,   90.00 ,     None,     None, 0.01    , 1), # 5
      'LON' : (   6,    0.00 ,  359.99 , -179.99 ,  180.00 , 0.01    , 1), # 6
       'IM' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 7
     'ATTC' : (   1,    0.   ,   35.   ,     None,     None, 1.      , 2), # 8
       'TI' : (   1,    0.   ,    3.   ,     None,     None, 1.      , 1), # 9
       'LI' : (   1,    0.   ,    6.   ,     None,     None, 1.      , 1), # 10
       'DS' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 11
       'VS' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 12
      'NID' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 13
       'II' : (   2,    0.   ,   10.   ,     None,     None, 1.      , 1), # 14
       'ID' : (   9,   32.   ,  126.   ,     None,     None,     None, 3), # 15
       'C1' : (   2,   48.   ,   57.   ,   65.   ,   90.   ,     None, 3), # 16
       'DI' : (   1,    0.   ,    6.   ,     None,     None, 1.      , 1), # 17
        'D' : (   3,    1.   ,  362.   ,     None,     None, 1.      , 1), # 18
       'WI' : (   1,    0.   ,    8.   ,     None,     None, 1.      , 1), # 19
        'W' : (   3,    0.0  ,   99.9  ,     None,     None, 0.1     , 1), # 20
       'VI' : (   1,    0.   ,    2.   ,     None,     None, 1.      , 1), # 21
       'VV' : (   2,   90.   ,   99.   ,     None,     None, 1.      , 1), # 22
       'WW' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 23
       'W1' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 24
      'SLP' : (   5,  870.0  , 1074.6  ,     None,     None, 0.1     , 1), # 25
        'A' : (   1,    0.   ,    8.   ,     None,     None, 1.      , 1), # 26
      'PPP' : (   3,    0.0  ,   51.0  ,     None,     None, 0.1     , 1), # 27
       'IT' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 28
       'AT' : (   4,  -99.9  ,   99.9  ,     None,     None, 0.1     , 1), # 29
     'WBTI' : (   1,    0.   ,    3.   ,     None,     None, 1.      , 1), # 30
      'WBT' : (   4,  -99.9  ,   99.9  ,     None,     None, 0.1     , 1), # 31
     'DPTI' : (   1,    0.   ,    3.   ,     None,     None, 1.      , 1), # 32
      'DPT' : (   4,  -99.9  ,   99.9  ,     None,     None, 0.1     , 1), # 33
       'SI' : (   2,    0.   ,   12.   ,     None,     None, 1.      , 1), # 34
      'SST' : (   4,  -99.9  ,   99.9  ,     None,     None, 0.1     , 1), # 35
        'N' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 36
       'NH' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 37
       'CL' : (   1,    0.   ,   10.   ,     None,     None, 1.      , 2), # 38
       'HI' : (   1,    0.   ,    1.   ,     None,     None, 1.      , 1), # 39
        'H' : (   1,    0.   ,   10.   ,     None,     None, 1.      , 2), # 40
       'CM' : (   1,    0.   ,   10.   ,     None,     None, 1.      , 2), # 41
       'CH' : (   1,    0.   ,   10.   ,     None,     None, 1.      , 2), # 42
       'WD' : (   2,    0.   ,   38.   ,     None,     None, 1.      , 1), # 43
       'WP' : (   2,    0.   ,   30.   ,   99.   ,   99.   , 1.      , 1), # 44
       'WH' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 45
       'SD' : (   2,    0.   ,   38.   ,     None,     None, 1.      , 1), # 46
       'SP' : (   2,    0.   ,   30.   ,   99.   ,   99.   , 1.      , 1), # 47
       'SH' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 48
        }

#
# ICOADS ATTACHMENT
#

attachment['01'] = 'ICOADS ATTACHMENT'

# List of parameters in ICOADS ATTACHMENT section
# In the order they are in on disc
parameters['01'] = ('BSI','B10','B1','DCK','SID','PT','DUPS','DUPC','TC','PB','WX','SX','C2','SQZ','SQA','AQZ','AQA','UQZ','UQA','VQZ','VQA','PQZ','PQA','DQZ','DQA','ND','SF','AF','UF','VF','PF','RF','ZNC','WNC','BNC','XNC','YNC','PNC','ANC','GNC','DNC','SNC','CNC','ENC','FNC','TNC','QCE','LZ','QCZ')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['01'] = {
      'BSI' : (   1,     None,     None,     None,     None, 1.      , 1), # 51
      'B10' : (   3,    1.   ,  648.   ,     None,     None, 1.      , 1), # 52
       'B1' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 53
      'DCK' : (   3,    0.   ,  999.   ,     None,     None, 1.      , 1), # 54
      'SID' : (   3,    0.   ,  999.   ,     None,     None, 1.      , 1), # 55
       'PT' : (   2,    0.   ,   21.   ,     None,     None, 1.      , 1), # 56
     'DUPS' : (   2,    0.   ,   14.   ,     None,     None, 1.      , 1), # 57
     'DUPC' : (   1,    0.   ,    2.   ,     None,     None, 1.      , 1), # 58
       'TC' : (   1,    0.   ,    1.   ,     None,     None, 1.      , 1), # 59
       'PB' : (   1,    0.   ,    2.   ,     None,     None, 1.      , 1), # 60
       'WX' : (   1,    1.   ,    1.   ,     None,     None, 1.      , 1), # 61
       'SX' : (   1,    1.   ,    1.   ,     None,     None, 1.      , 1), # 62
       'C2' : (   2,    0.   ,   40.   ,     None,     None, 1.      , 1), # 63
      'SQZ' : (   1,    1.   ,   35.   ,     None,     None, 1.      , 2), # 64
      'SQA' : (   1,    1.   ,   21.   ,     None,     None, 1.      , 2), # 65
      'AQZ' : (   1,    1.   ,   35.   ,     None,     None, 1.      , 2), # 66
      'AQA' : (   1,    1.   ,   21.   ,     None,     None, 1.      , 2), # 67
      'UQZ' : (   1,    1.   ,   35.   ,     None,     None, 1.      , 2), # 68
      'UQA' : (   1,    1.   ,   21.   ,     None,     None, 1.      , 2), # 69
      'VQZ' : (   1,    1.   ,   35.   ,     None,     None, 1.      , 2), # 70
      'VQA' : (   1,    1.   ,   21.   ,     None,     None, 1.      , 2), # 71
      'PQZ' : (   1,    1.   ,   35.   ,     None,     None, 1.      , 2), # 72
      'PQA' : (   1,    1.   ,   21.   ,     None,     None, 1.      , 2), # 73
      'DQZ' : (   1,    1.   ,   35.   ,     None,     None, 1.      , 2), # 74
      'DQA' : (   1,    1.   ,   21.   ,     None,     None, 1.      , 2), # 75
       'ND' : (   1,    1.   ,    2.   ,     None,     None, 1.      , 1), # 76
       'SF' : (   1,    1.   ,   15.   ,     None,     None, 1.      , 2), # 77
       'AF' : (   1,    1.   ,   15.   ,     None,     None, 1.      , 2), # 78
       'UF' : (   1,    1.   ,   15.   ,     None,     None, 1.      , 2), # 79
       'VF' : (   1,    1.   ,   15.   ,     None,     None, 1.      , 2), # 80
       'PF' : (   1,    1.   ,   15.   ,     None,     None, 1.      , 2), # 81
       'RF' : (   1,    1.   ,   15.   ,     None,     None, 1.      , 2), # 82
      'ZNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 83
      'WNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 84
      'BNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 85
      'XNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 86
      'YNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 87
      'PNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 88
      'ANC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 89
      'GNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 90
      'DNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 91
      'SNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 92
      'CNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 93
      'ENC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 94
      'FNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 95
      'TNC' : (   1,    1.   ,   10.   ,     None,     None, 1.      , 2), # 96
      'QCE' : (   2,    0.   ,   63.   ,     None,     None, 1.      , 1), # 97
       'LZ' : (   1,    1.   ,    1.   ,     None,     None, 1.      , 1), # 98
      'QCZ' : (   2,    0.   ,   31.   ,     None,     None, 1.      , 1), # 99
        }

#
# IMMT-5/FM13 ATTACHMENT
#

attachment['05'] = 'IMMT-5/FM13 ATTACHMENT'

# List of parameters in IMMT-5/FM13 ATTACHMENT section
# In the order they are in on disc
parameters['05'] = ('OS','OP','FM','IMMV','IX','W2','WMI','SD2','SP2','SH2','IS','ES','RS','IC1','IC2','IC3','IC4','IC5','IR','RRR','TR','NU','QCI','QI1','QI2','QI3','QI4','QI5','QI6','QI7','QI8','QI9','QI10','QI11','QI12','QI13','QI14','QI15','QI16','QI17','QI18','QI19','QI20','QI21','HDG','COG','SOG','SLL','SLHH','RWD','RWS','QI22','QI23','QI24','QI25','QI26','QI27','QI28','QI29','RH','RHI','AWSI','IMONO')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['05'] = {
       'OS' : (   1,    0.   ,    6.   ,     None,     None, 1.      , 1), # 102
       'OP' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 103
       'FM' : (   1,    0.   ,   35.   ,     None,     None, 1.      , 2), # 104
     'IMMV' : (   1,    0.   ,   35.   ,     None,     None, 1.      , 2), # 105
       'IX' : (   1,    1.   ,    7.   ,     None,     None, 1.      , 1), # 106
       'W2' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 107
      'WMI' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 108
      'SD2' : (   2,    0.   ,   38.   ,     None,     None, 1.      , 1), # 109
      'SP2' : (   2,    0.   ,   30.   ,   99.   ,   99.   , 1.      , 1), # 110
      'SH2' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 111
       'IS' : (   1,    1.   ,    5.   ,     None,     None, 1.      , 1), # 112
       'ES' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 113
       'RS' : (   1,    0.   ,    4.   ,     None,     None, 1.      , 1), # 114
      'IC1' : (   1,    0.   ,   10.   ,     None,     None, 1.      , 2), # 115
      'IC2' : (   1,    0.   ,   10.   ,     None,     None, 1.      , 2), # 116
      'IC3' : (   1,    0.   ,   10.   ,     None,     None, 1.      , 2), # 117
      'IC4' : (   1,    0.   ,   10.   ,     None,     None, 1.      , 2), # 118
      'IC5' : (   1,    0.   ,   10.   ,     None,     None, 1.      , 2), # 119
       'IR' : (   1,    0.   ,    4.   ,     None,     None, 1.      , 1), # 120
      'RRR' : (   3,    0.   ,  999.   ,     None,     None, 1.      , 1), # 121
       'TR' : (   1,    1.   ,    9.   ,     None,     None, 1.      , 1), # 122
       'NU' : (   1,   32.   ,  126.   ,     None,     None,     None, 3), # 123
      'QCI' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 124
      'QI1' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 125
      'QI2' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 126
      'QI3' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 127
      'QI4' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 128
      'QI5' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 129
      'QI6' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 130
      'QI7' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 131
      'QI8' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 132
      'QI9' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 133
     'QI10' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 134
     'QI11' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 135
     'QI12' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 136
     'QI13' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 137
     'QI14' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 138
     'QI15' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 139
     'QI16' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 140
     'QI17' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 141
     'QI18' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 142
     'QI19' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 143
     'QI20' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 144
     'QI21' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 145
      'HDG' : (   3,    0.   ,  360.   ,     None,     None, 1.      , 1), # 146
      'COG' : (   3,    0.   ,  360.   ,     None,     None, 1.      , 1), # 147
      'SOG' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 148
      'SLL' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 149
     'SLHH' : (   3,  -99.   ,   99.   ,     None,     None, 1.      , 1), # 150
      'RWD' : (   3,    1.   ,  362.   ,     None,     None, 1.      , 1), # 151
      'RWS' : (   3,    0.0  ,   99.9  ,     None,     None, 0.1     , 1), # 152
     'QI22' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 153
     'QI23' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 154
     'QI24' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 155
     'QI25' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 156
     'QI26' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 157
     'QI27' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 158
     'QI28' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 159
     'QI29' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 160
       'RH' : (   4,    0.0  ,  100.0  ,     None,     None, 0.1     , 1), # 161
      'RHI' : (   1,    0.   ,    4.   ,     None,     None, 1.      , 1), # 162
     'AWSI' : (   1,    0.   ,    2.   ,     None,     None, 1.      , 1), # 163
    'IMONO' : (   7,    0.   ,9999999. ,     None,     None, 1.      , 1), # 164
        }

#
# MODEL QUALITY CONTROL ATTACHMENT
#

attachment['06'] = 'MODEL QUALITY CONTROL ATTACHMENT'

# List of parameters in MODEL QUALITY CONTROL ATTACHMENT section
# In the order they are in on disc
parameters['06'] = ('CCCC','BUID','FBSRC','BMP','BSWU','SWU','BSWV','SWV','BSAT','BSRH','SRH','BSST','MST','MSH','BY','BM','BD','BH','BFL')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['06'] = {
     'CCCC' : (   4,   65.   ,   90.   ,     None,     None,     None, 3), # 167
     'BUID' : (   6,   48.   ,   57.   ,   65.   ,   90.   ,     None, 3), # 168
    'FBSRC' : (   1,    0.   ,    0.   ,     None,     None, 1.      , 1), # 169
      'BMP' : (   5,  870.0  , 1074.6  ,     None,     None, 0.1     , 1), # 170
     'BSWU' : (   4,  -99.9  ,   99.9  ,     None,     None, 0.1     , 1), # 171
      'SWU' : (   4,  -99.9  ,   99.9  ,     None,     None, 0.1     , 1), # 172
     'BSWV' : (   4,  -99.9  ,   99.9  ,     None,     None, 0.1     , 1), # 173
      'SWV' : (   4,  -99.9  ,   99.9  ,     None,     None, 0.1     , 1), # 174
     'BSAT' : (   4,  -99.9  ,   99.9  ,     None,     None, 0.1     , 1), # 175
     'BSRH' : (   3,    0.   ,  100.   ,     None,     None, 1.      , 1), # 176
      'SRH' : (   3,    0.   ,  100.   ,     None,     None, 1.      , 1), # 177
     'BSST' : (   5, -99.99  ,  99.99  ,     None,     None, 0.01    , 1), # 178
      'MST' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 179
      'MSH' : (   4, -999.   , 9999.   ,     None,     None, 1.      , 1), # 180
       'BY' : (   4,    0.   , 9999.   ,     None,     None, 1.      , 1), # 181
       'BM' : (   2,    1.   ,   12.   ,     None,     None, 1.      , 1), # 182
       'BD' : (   2,    1.   ,   31.   ,     None,     None, 1.      , 1), # 183
       'BH' : (   2,    0.   ,   23.   ,     None,     None, 1.      , 1), # 184
      'BFL' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 185
        }

#
# SHIP METADATA ATTACHMENT
#

attachment['07'] = 'SHIP METADATA ATTACHMENT'

# List of parameters in SHIP METADATA ATTACHMENT section
# In the order they are in on disc
parameters['07'] = ('MDS','C1M','OPM','KOV','COR','TOB','TOT','EOT','LOT','TOH','EOH','SIM','LOV','DOS','HOP','HOT','HOB','HOA','SMF','SME','SMV')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['07'] = {
      'MDS' : (   1,    0.   ,    2.   ,     None,     None, 1.      , 1), # 188
      'C1M' : (   2,   65.   ,   90.   ,     None,     None,     None, 3), # 189
      'OPM' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 190
      'KOV' : (   2,   32.   ,  126.   ,     None,     None,     None, 3), # 191
      'COR' : (   2,   65.   ,   90.   ,     None,     None,     None, 3), # 192
      'TOB' : (   3,   32.   ,  126.   ,     None,     None,     None, 3), # 193
      'TOT' : (   3,   32.   ,  126.   ,     None,     None,     None, 3), # 194
      'EOT' : (   2,   32.   ,  126.   ,     None,     None,     None, 3), # 195
      'LOT' : (   2,   32.   ,  126.   ,     None,     None,     None, 3), # 196
      'TOH' : (   1,   32.   ,  126.   ,     None,     None,     None, 3), # 197
      'EOH' : (   2,   32.   ,  126.   ,     None,     None,     None, 3), # 198
      'SIM' : (   3,   32.   ,  126.   ,     None,     None,     None, 3), # 199
      'LOV' : (   3,    0.   ,  999.   ,     None,     None, 1.      , 1), # 200
      'DOS' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 201
      'HOP' : (   3,    0.   ,  999.   ,     None,     None, 1.      , 1), # 202
      'HOT' : (   3,    0.   ,  999.   ,     None,     None, 1.      , 1), # 203
      'HOB' : (   3,    0.   ,  999.   ,     None,     None, 1.      , 1), # 204
      'HOA' : (   3,    0.   ,  999.   ,     None,     None, 1.      , 1), # 205
      'SMF' : (   5,    0.   ,99999.   ,     None,     None, 1.      , 1), # 206
      'SME' : (   5,    0.   ,99999.   ,     None,     None, 1.      , 1), # 207
      'SMV' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 208
        }

#
# NEAR-SURFACE OCEANOGRAPHIC DATA ATTACHMENT
#

attachment['08'] = 'NEAR-SURFACE OCEANOGRAPHIC DATA ATTACHMENT'

# List of parameters in NEAR-SURFACE OCEANOGRAPHIC DATA ATTACHMENT section
# In the order they are in on disc
parameters['08'] = ('OTV','OTZ','OSV','OSZ','OOV','OOZ','OPV','OPZ','OSIV','OSIZ','ONV','ONZ','OPHV','OPHZ','OCV','OCZ','OAV','OAZ','OPCV','OPCZ','ODV','ODZ','PUID')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['08'] = {
      'OTV' : (   5,  -3.000 ,  38.999 ,     None,     None, 0.001   , 1), # 211
      'OTZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 212
      'OSV' : (   5,   0.000 ,  40.999 ,     None,     None, 0.001   , 1), # 213
      'OSZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 214
      'OOV' : (   4,    0.00 ,   12.99 ,     None,     None, 0.01    , 1), # 215
      'OOZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 216
      'OPV' : (   4,    0.00 ,   30.99 ,     None,     None, 0.01    , 1), # 217
      'OPZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 218
     'OSIV' : (   5,    0.00 ,  250.99 ,     None,     None, 0.01    , 1), # 219
     'OSIZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 220
      'ONV' : (   5,    0.00 ,  500.99 ,     None,     None, 0.01    , 1), # 221
      'ONZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 222
     'OPHV' : (   3,    6.20 ,    9.20 ,     None,     None, 0.01    , 1), # 223
     'OPHZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 224
      'OCV' : (   4,    0.00 ,   50.99 ,     None,     None, 0.01    , 1), # 225
      'OCZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 226
      'OAV' : (   3,    0.00 ,    3.10 ,     None,     None, 0.01    , 1), # 227
      'OAZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 228
     'OPCV' : (   4,    0.0  ,  999.0  ,     None,     None, 0.1     , 1), # 229
     'OPCZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 230
      'ODV' : (   2,    0.0  ,    4.0  ,     None,     None, 0.1     , 1), # 231
      'ODZ' : (   4,    0.00 ,   99.99 ,     None,     None, 0.01    , 1), # 232
     'PUID' : (  10,   32.   ,  126.   ,     None,     None,     None, 3), # 233
        }

#
# EDITED CLOUD REPORT ATTACHMENT
#

attachment['09'] = 'EDITED CLOUD REPORT ATTACHMENT'

# List of parameters in EDITED CLOUD REPORT ATTACHMENT section
# In the order they are in on disc
parameters['09'] = ('CCE','WWE','NE','NHE','HE','CLE','CME','CHE','AM','AH','UM','UH','SBI','SA','RI')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['09'] = {
      'CCE' : (   1,    0.   ,   13.   ,     None,     None, 1.      , 2), # 236
      'WWE' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 237
       'NE' : (   1,    0.   ,    8.   ,     None,     None, 1.      , 1), # 238
      'NHE' : (   1,    0.   ,    8.   ,     None,     None, 1.      , 1), # 239
       'HE' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 240
      'CLE' : (   2,    0.   ,   11.   ,     None,     None, 1.      , 1), # 241
      'CME' : (   2,    0.   ,   12.   ,     None,     None, 1.      , 1), # 242
      'CHE' : (   1,    0.   ,    9.   ,     None,     None, 1.      , 1), # 243
       'AM' : (   3,    0.   ,    8.00 ,     None,     None, 0.01    , 1), # 244
       'AH' : (   3,    0.   ,    8.00 ,     None,     None, 0.01    , 1), # 245
       'UM' : (   1,    0.   ,    8.   ,     None,     None, 1.      , 1), # 246
       'UH' : (   1,    0.   ,    8.   ,     None,     None, 1.      , 1), # 247
      'SBI' : (   1,    0.   ,    1.   ,     None,     None, 1.      , 1), # 248
       'SA' : (   4,  -90.0  ,   90.0  ,     None,     None, 0.1     , 1), # 249
       'RI' : (   4,   -1.10 ,    1.17 ,     None,     None, 0.01    , 1), # 250
        }

#
# REANALYSES QC/FEEDBACK ATTACHMENT
#

attachment['95'] = 'REANALYSES QC/FEEDBACK ATTACHMENT'

# List of parameters in REANALYSES QC/FEEDBACK ATTACHMENT section
# In the order they are in on disc
parameters['95'] = ('ICNR','FNR','DPRO','DPRP','UFR','MFGR','MFGSR','MAR','MASR','BCR','ARCR','CDR','ASIR')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['95'] = {
     'ICNR' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 253
      'FNR' : (   2,    1.   ,   99.   ,     None,     None, 1.      , 1), # 254
     'DPRO' : (   2,    1.   ,   99.   ,     None,     None, 1.      , 1), # 255
     'DPRP' : (   2,    1.   ,   99.   ,     None,     None, 1.      , 1), # 256
      'UFR' : (   1,    1.   ,    6.   ,     None,     None, 1.      , 1), # 257
     'MFGR' : (   7,-999999. ,9999999. ,     None,     None, 1.      , 1), # 258
    'MFGSR' : (   7,-999999. ,9999999. ,     None,     None, 1.      , 1), # 259
      'MAR' : (   7,-999999. ,9999999. ,     None,     None, 1.      , 1), # 260
     'MASR' : (   7,-999999. ,9999999. ,     None,     None, 1.      , 1), # 261
      'BCR' : (   7,-999999. ,9999999. ,     None,     None, 1.      , 1), # 262
     'ARCR' : (   4,   48.   ,   57.   ,   65.   ,   90.   ,     None, 3), # 263
      'CDR' : (   8,   48.   ,   57.   ,     None,     None,     None, 3), # 264
     'ASIR' : (   1,    0.   ,    1.   ,     None,     None, 1.      , 1), # 265
        }

#
# ICOADS VALUE-ADDED DATABASE ATTACHMENT
#

attachment['96'] = 'ICOADS VALUE-ADDED DATABASE ATTACHMENT'

# List of parameters in ICOADS VALUE-ADDED DATABASE ATTACHMENT section
# In the order they are in on disc
parameters['96'] = ('ICNI','FNI','JVAD','VAD','IVAU1','JVAU1','VAU1','IVAU2','JVAU2','VAU2','IVAU3','JVAU3','VAU3','VQC','ARCI','CDI','ASII')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['96'] = {
     'ICNI' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 268
      'FNI' : (   2,    1.   ,   99.   ,     None,     None, 1.      , 1), # 269
     'JVAD' : (   1,    0.   ,   35.   ,     None,     None, 1.      , 2), # 270
      'VAD' : (   6,-99999.  ,999999.  ,     None,     None, 1.      , 1), # 271
    'IVAU1' : (   1,    1.   ,   35.   ,     None,     None, 1.      , 2), # 272
    'JVAU1' : (   1,    0.   ,   35.   ,     None,     None, 1.      , 2), # 273
     'VAU1' : (   6,-99999.  ,999999.  ,     None,     None, 1.      , 1), # 274
    'IVAU2' : (   1,    1.   ,   35.   ,     None,     None, 1.      , 2), # 275
    'JVAU2' : (   1,    0.   ,   35.   ,     None,     None, 1.      , 2), # 276
     'VAU2' : (   6,-99999.  ,999999.  ,     None,     None, 1.      , 1), # 277
    'IVAU3' : (   1,    1.   ,   35.   ,     None,     None, 1.      , 2), # 278
    'JVAU3' : (   1,    0.   ,   35.   ,     None,     None, 1.      , 2), # 279
     'VAU3' : (   6,-99999.  ,999999.  ,     None,     None, 1.      , 1), # 280
      'VQC' : (   1,    1.   ,    4.   ,    9.   ,    9.   , 1.      , 1), # 281
     'ARCI' : (   4,   48.   ,   57.   ,   65.   ,   90.   ,     None, 3), # 282
      'CDI' : (   8,   48.   ,   57.   ,     None,     None,     None, 3), # 283
     'ASII' : (   1,    0.   ,    1.   ,     None,     None, 1.      , 1), # 284
        }

#
# ERROR ATTACHMENT
#

attachment['97'] = 'ERROR ATTACHMENT'

# List of parameters in ERROR ATTACHMENT section
# In the order they are in on disc
parameters['97'] = ('ICNE','FNE','CEF','ERRD','ARCE','CDE','ASIE')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['97'] = {
     'ICNE' : (   2,    0.   ,   99.   ,     None,     None, 1.      , 1), # 287
      'FNE' : (   2,    1.   ,   99.   ,     None,     None, 1.      , 1), # 288
      'CEF' : (   1,    0.   ,    1.   ,     None,     None, 1.      , 1), # 289
     'ERRD' : (  10,   32.   ,  126.   ,     None,     None,     None, 3), # 290
     'ARCE' : (   4,   48.   ,   57.   ,   65.   ,   90.   ,     None, 3), # 291
      'CDE' : (   8,   48.   ,   57.   ,     None,     None,     None, 3), # 292
     'ASIE' : (   1,    0.   ,    1.   ,     None,     None, 1.      , 1), # 293
        }

#
# UNIQUE ID ATTACHMENT
#

attachment['98'] = 'UNIQUE ID ATTACHMENT'

# List of parameters in UNIQUE ID ATTACHMENT section
# In the order they are in on disc
parameters['98'] = ('UID','RN1','RN2','RN3','RSA','IRF')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['98'] = {
      'UID' : (   6,   48.   ,   57.   ,   65.   ,   90.   ,     None, 3), # 296
      'RN1' : (   1,    0.   ,   35.   ,     None,     None, 1.      , 2), # 297
      'RN2' : (   1,    0.   ,   35.   ,     None,     None, 1.      , 2), # 298
      'RN3' : (   1,    0.   ,   35.   ,     None,     None, 1.      , 2), # 299
      'RSA' : (   1,    0.   ,    2.   ,     None,     None, 1.      , 1), # 300
      'IRF' : (   1,    0.   ,    2.   ,     None,     None, 1.      , 1), # 301
        }

#
# SUPPLEMENTAL DATA ATTACHMENT
#

attachment['99'] = 'SUPPLEMENTAL DATA ATTACHMENT'

# List of parameters in SUPPLEMENTAL DATA ATTACHMENT section
# In the order they are in on disc
parameters['99'] = ('ATTE','SUPD')
# For each parameter, provide an array specifying:
#    Its length in bytes, on disc,
#    Its minimum value
#    Its maximum value
#    Its minimum value (alternative representation)
#    Its maximum value (alternative representation)
#    Its units scale
#    Its encoding (1 = integer, 3= character, 2= base36)
definitions['99'] = {
     'ATTE' : (   1,    0.   ,    2.   ,     None,     None, 1.      , 1), # 304
     'SUPD' : (1024,   32.   ,  126.   ,     None,     None,     None, 3), # 305
        }



