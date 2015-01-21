#! /usr/bin/env python

"""
atom efficiency combinator
"""

__author__ = "A.Weiler"
__version__ = "0.1"


# List of changes
#   01/21/15: first commit (AW)
#
# TODO:
#   - check which version of ATOM has been used to ensure compatibility of out yaml!
#   - feature: allow user to restrict to particular analysis?
#   - add flags if not present (done)


import logging
import yaml
import argparse 

import os
import sys

if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s:  %(message)s', level=logging.INFO)

    parser = argparse.ArgumentParser( 
                description='Atom efficiency combinator: Combines atom yaml files.')

    requiredNamed = parser.add_argument_group('required arguments')

    requiredNamed.add_argument('-f', action='append', dest='inputfileList',
                    default=[],
                    help='Add all input files. E.g. -f file1.yml -f file2.yml etc.',
                    required=True
                    )
    requiredNamed.add_argument("-o", "--output", dest="outfilename", default=[],
                       help="write Atom Limit output to file", 
                       metavar="EFFCOMBINATION", required=True)
    args = parser.parse_args()

    print args.inputfileList

    # logging.info('Reading Atom file <' + args.inputfile + ">...")    

    fileList = args.inputfileList

    AtomData = []

    for fileN in fileList:
        logging.info('Reading Atom file <' + fileN + "> ...")
        try:
            stream = open(fileN, 'r')
        except:
            logging.error("Invalid filename " + fileN)
            exit()
        try:
            AtomData.append(yaml.load(stream,Loader=yaml.CLoader)) # Loader=yaml.CLoader
            stream.close()
        except:
            AtomData.append(yaml.load(stream)) # Loader=yaml.CLoader
            logging.warning("Using slower python yaml reader. Please install libyaml for faster processing.")
            stream.close()

        AtomRunInfo = yaml.dump(AtomData, default_flow_style=False) 
        #print AtomRunInfo

    if len(AtomData) < 2:
        logging.warning("Only one Atom output file given. Cannot combine writing input to output file.")
        AtomOut = yaml.dump(AtomData[0], default_flow_style=False)   
        print args.outfilename
        with open(args.outfilename, 'w') as outFileStream:
             outFileStream.write(AtomOut)
        exit()
        
    AtomDefault = AtomData[0]

    AtomData.pop(0)


    # better do this with hashes in the future ... 

    for atomAdd in AtomData:
        for anaName in AtomDefault["Analyses"].keys():
            #print anaName, AtomDefault["Analyses"][anaName]
            effIndDefault = 0
            for effEntryDefault in AtomDefault["Analyses"][anaName]["Efficiencies"]:
                dataIndDefault = 0
                for subEffEntryDefault in effEntryDefault["Data"]:
                    
                    for effEntryAdd in atomAdd["Analyses"][anaName]["Efficiencies"]:
                        for subEffEntryAdd in effEntryAdd["Data"]:
                            try:
                                test = atomAdd["Analyses"][anaName]["Efficiencies"][effIndDefault]["Data"][dataIndDefault]["Efficiency Value"]
                            except:
                                logging.error("Atom outputs do not have the same structure! Please make sure to book cuts and efficiencies. In void init() of the analysis source, add\n bookEfficiency(\"EfficiencyName\");\n bookCut(\"CutName\");" )
                                exit()
                            if subEffEntryAdd["Sub-process ID"] == subEffEntryDefault["Sub-process ID"] and \
                               effEntryDefault["Efficiency Name"] == effEntryAdd["Efficiency Name"]:
                                #print subEffEntryAdd, subEffEntryDefault
                                defval = subEffEntryDefault["Efficiency Value"]
                                addval = subEffEntryAdd["Efficiency Value"]

                                [adderrM,adderrP]  = subEffEntryAdd["Efficiency Stat Error"]
                                [deferrM,deferrP]  = subEffEntryDefault["Efficiency Stat Error"]
                                
                                deferror = 1/2. * ( -deferrM + deferrP ) 
                                adderror = 1/2. * ( -adderrM + adderrP )

                                # Efficiency combination:
                                # \epsilon_{A+B} = \frac{\sigma_B^2 \epsilon_A + \sigma_A^2 \epsilon_B}{\sigma_A^2+ \sigma_B^2 }

                                # New error combination:
                                #   delEps_{tot} = 1/sqrt( 1/delEff1^2 + 1/delEff2^2)

                                effNew = ((deferror**2 * addval + adderror**2 * defval ) / (deferror**2 + adderror**2)) 
                                effStatErrorNew = 1/(1./ deferror**2 + 1./adderror**2  ) ** (0.5)

                                print "ana, effname, procID, defval, addval, effNew, deferror, adderror,effStatErrorNew"
                                print anaName, effEntryDefault["Efficiency Name"], subEffEntryAdd["Sub-process ID"], defval, addval, effNew, deferror, adderror,effStatErrorNew
                                AtomDefault["Analyses"][anaName]["Efficiencies"][effIndDefault]["Data"][dataIndDefault]["Efficiency Value"] = effNew
                                AtomDefault["Analyses"][anaName]["Efficiencies"][effIndDefault]["Data"][dataIndDefault]["Efficiency Stat Error"] = [-effStatErrorNew,effStatErrorNew]

                                # merge flags

                                mergedFlags = list(set(subEffEntryDefault["Flags"] + subEffEntryAdd["Flags"]))

                                #print mergedFlags
                                AtomDefault["Analyses"][anaName]["Efficiencies"][effIndDefault]["Data"][dataIndDefault]["Flags"] = mergedFlags

                    dataIndDefault += 1
                effIndDefault += 1            
                        
    logging.info('Writin combined Atom file <' + args.outfilename + "> ...")
    with open(args.outfilename, 'w') as outFileStream:
        AtomOut = yaml.dump(AtomDefault, default_flow_style=False)   
        outFileStream.write(AtomOut)
    exit()