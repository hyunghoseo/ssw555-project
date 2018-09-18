import sys

# dict of level-to-tags
tags = {"0": ["INDI","FAM","HEAD","TRLR","NOTE"],
        "1": ["NAME","SEX","BIRT","DEAT","FAMC","FAMS","MARR","HUSB","WIFE",
              "CHIL","DIV"],
        "2": ["DATE"]}

indiList = []
famList = []
        
def main(fname):
    with open(fname) as f:
        entry = {} 
        type = "" # INDI, FAM
        expectsDate = 0
        dateType = "" # birth, death, marr, div
        for line in f.readlines():
            tokens = line.split()
            if len(tokens) == 0:
                continue
                
            level, tag, valid, args = verify_line(tokens)
            
            if valid == "N":
                continue
            
            if tag in ["NOTE", "HEAD", "TRLR"]:
                continue
            
            if entry and tag in ["INDI", "FAM"]:
                if type == "INDI":
                    indiList.append(entry)
                elif type == "FAM":
                    famList.append(entry)
                entry = {}
                
            if expectsDate:
                expectsDate = 0
                if tag == "DATE":
                    entry[dateType] = args
                    continue
                
            if not entry.get("id"):
                if tag == "INDI":
                    type = "INDI"
                    entry["id"] = args
                elif tag == "FAM":
                    type = "FAM"
                    entry["id"] = args
            elif type == "INDI":
                if tag == "NAME":
                    entry["name"] = args
                elif tag == "SEX":
                    entry["sex"] = args
                elif tag == "BIRT":
                    expectsDate = 1
                    dateType = "birth"
                elif tag == "DEAT":
                    expectsDate = 1
                    dateType = "death"
                elif tag == "FAMC":
                    entry["famc"] = args
                elif tag == "FAMS":
                    if entry.get("fams"):
                        entry["fams"].append(args)
                    else:
                        entry["fams"] = [args]
            elif type == "FAM":
                if tag == "MARR":
                    expectsDate = 1
                    dateType = "marr"
                elif tag == "HUSB":
                    entry["husb"] = args
                elif tag == "WIFE":
                    entry["wife"] = args
                elif tag == "CHIL":
                    if entry.get("children"):
                        entry["children"].append(args)
                    else:
                        entry["children"] = [args]
                elif tag == "DIV":
                    expectsDate = 1
                    dateType = "div"
           
                
                    
        if type == "INDI":
            indiList.append(entry)
        if type == "FAM":
            famList.append(entry)
            
        print indiList
        print famList
            

def verify_line(tokens):
    # print "-->", line.rstrip("\n")
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

    # print "<-- {}|{}|{}|{}".format(level,tag,valid,arguments)
    return [level,tag,valid,arguments]

if __name__ == "__main__":
    try:
        fname = sys.argv[1]
    except IndexError:
        print "Usage: run.py [.ged file]"
        exit()
        
    try:
        main(fname)
    except IOError:
        print "No such file:", fname
