import sys

# dict of level-to-tags
tags = {"0": ["INDI","FAM","HEAD","TRLR","NOTE"],
        "1": ["NAME","SEX","BIRT","DEAT","FAMC","FAMS","MARR","HUSB","WIFE",
              "CHIL","DIV"],
        "2": ["DATE"]}

def main(fname):
    with open(fname) as f:
        for line in f.readlines():
            tokens = line.split()
            if len(tokens) == 0:
                continue
            print "-->", line.rstrip("\n")
            valid = "Y"
            level = tokens[0]

            if len(tokens) > 2 and tokens[2] in ["INDI", "FAM"]:
                tag = tokens[2]
                arguments = tokens[1]
            else:
                try:
                    tag = tokens[1]
                except IndexError:
                    valid = "N"
                if tag in ["INDI", "FAM"]:
                    valid = "N"
                try:
                    arguments = " ".join(tokens[2:])
                except IndexError:
                    arguments = ""
                
            # check that the tag and level are valid
            if tag not in tags.get(level,[]):
                valid = "N"

            print "<-- {}|{}|{}|{}".format(level,tag,valid,arguments)

if __name__ == "__main__":
    try:
        fname = sys.argv[1]
    except IndexError:
        print "Usage: run.py [.ged file]"
    main(fname)
