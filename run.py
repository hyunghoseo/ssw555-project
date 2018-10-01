import sys
from datetime import datetime, date
from prettytable import PrettyTable

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
                add_entry(entry, type)
                entry = {}
                
            if expectsDate:
                expectsDate = 0
                if tag == "DATE":
                    date = datetime.strptime(args, "%d %b %Y")
                    entry[dateType] = date
                    entry[dateType + "Str"] = date.strftime("%Y-%m-%d")
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
                    
        add_entry(entry, type)
            
        print_indi_table()
        print_fam_table()
            
def add_entry(entry, type):
    if type == "INDI":
        if entry.get("birth"):
            if entry.get("death"):
                age = get_age(entry["birth"], entry["death"])
                if age < 0:
                    raise Exception("INDI {} has death date before birth date".format(entry["id"]))
                else:
                    entry["age"] = age
            else:
                entry["age"] = get_age(entry["birth"], date.today())
            if entry.get("marr"):
                if get_age(entry["birth"], entry["marr"]) < 0:
                    raise Exception ("INDI {} has a marriage date before birth date".format(entry["id"]))
        else:
            raise Exception("INDI {} is missing a birth date".format(entry["id"]))
        indiList.append(entry)
    if type == "FAM":
        if entry.get("div") and entry.get("marr") and (get_age(entry.get("marr"),entry.get("div")) < 0):
            print "Error: FAM " + entry["id"] + ": marriage occurred after divorce"
        if entry.get("marr") and entry.get("husb") and entry.get("wife"):
            husb = get_indi(entry['husb'])
            wif = get_indi(entry['wife'])
            if (husb.get("gender") != "M"):
                print "Error: FAM " + entry["id"] + ": Husband is not male"
            if (wif.get("gender") != "F"):
                print "Error: FAM " + entry["id"] + ": Wife is not female"
            if (husb.get("death") and get_age(entry.get("marr"),husb["death"]) < 0) or (wif.get("death") and get_age(entry.get("marr"),wif["death"]) < 0):
                print "Error: FAM " + entry["id"] + ": marriage occurred after death of one of the spouses"

        famList.append(entry)

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
    
def print_indi_table():
    t = PrettyTable()
    t.field_names = ["ID","Name","Gender","Birthday","Age","Alive","Death","Child","Spouse"]
    for indi in indiList:
        t.add_row([ indi.get("id","NA"),
                    indi.get("name","NA"),
                    indi.get("sex","NA"),
                    indi.get("birthStr","NA"),
                    indi.get("age","NA"),
                    "False" if indi.get("death") else "True",
                    indi.get("deathStr","NA"),
                    indi.get("famc","None"),
                    indi.get("fams","NA")
                  ])
    print "Indivudals\n", t
                  
def print_fam_table():
    t = PrettyTable()
    t.field_names = ["ID","Married","Divorced","Husband ID","Husband Name","Wife ID","Wife Name","Children"]
    for fam in famList:
        t.add_row([ fam.get("id","NA"),
                    fam.get("marrStr","NA"),
                    fam.get("divStr","NA"),
                    fam.get("husb","NA"),
                    get_indi(fam.get("husb")).get("name"),
                    fam.get("wife","NA"),
                    get_indi(fam.get("wife")).get("name"),
                    fam.get("children","NA")
                  ])
    print "Families\n", t

def get_indi(id):
    return next((indi for indi in indiList if indi["id"] == id), {})

def get_fam(id):
    return next((fam for fam in famList if fam["id"] == id), {})
    
def get_age(birth, death):
    return death.year - birth.year - ((death.month, death.day) < (birth.month, birth.day))


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
