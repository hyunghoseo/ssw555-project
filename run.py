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

        check_birth_before_marr()
        check_parents_age_valid()

        print_list_single()
        print_list_deceased()
            
        print_indi_table()
        print_fam_table()

def add_entry(entry, type):
    if type == "INDI":
        if entry.get("birth"):
            if entry.get("death"):
                age = get_age(entry["birth"], entry["death"])
                if age < 0:
                    print("Error: INDI {} has death date before birth date".format(entry["id"]))
                else:
                    entry["age"] = age
            else:
                entry["age"] = get_age(entry["birth"], date.today())
        else:
            print "Error: INDI {} is missing a birth date".format(entry["id"])
        indiList.append(entry)
    if type == "FAM":
        if entry.get("div") and entry.get("marr") and (get_age(entry.get("marr"),entry.get("div")) < 0):
            print "Error: FAM {} has marriage date occurred after divorce date".format(entry["id"])
        if entry.get("marr") and entry.get("husb") and entry.get("wife"):
            husb = get_indi(entry['husb'])
            wif = get_indi(entry['wife'])
            if (husb.get("sex") != "M"):
                print "Error: FAM {} has husband that is not male".format(entry["id"])
            if (wif.get("sex") != "F"):
                print "Error: FAM {} has wife that is not female".format(entry["id"])
            if (husb.get("death") and get_age(entry.get("marr"),husb["death"]) < 0) or (wif.get("death") and get_age(entry.get("marr"),wif["death"]) < 0):
                print "Error: FAM {} has marriage after death date of one of the spouses".format(entry["id"])

        famList.append(entry)

def check_parents_age_valid():
    for fam in famList:
        if fam.get("children"):
            childIdList = fam.get("children")
            fatherId = fam.get("husb")
            motherId = fam.get("wife")
            father = get_indi(fatherId)
            mother = get_indi(motherId)
            for childId in childIdList:
                child = get_indi(childId)
                if father.get("age") and mother.get("age") and child.get("age") and father["age"] - child["age"] >= 80 and mother["age"] - child["age"] >= 60:
                    print "Error: INDI's {} Father and Mother are over their respective age limits".format(child["id"])
                elif mother.get("age") and child.get("age") and mother["age"] - child["age"] >= 60:
                    print "Error: INDI's {} Mother is 60 years or older than him/her".format(child["id"])
                elif father.get("age") and child.get("age") and father["age"] - child["age"] >= 80:
                    print "Error: INDI's {} Father is 80 years or older than him/her".format(child["id"])

def check_birth_before_marr():
    for entry in indiList:
        famIdList = entry.get("fams")
        if famIdList:
            for famId in famIdList:
                fam = get_fam(famId)
                if get_age(entry["birth"], fam["marr"]) < 0:
                    print "Error: INDI {} has marriage date before birth date".format(entry["id"])

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

def print_list_single():
    temp_list = []
    for indi in indiList:
        if(indi.get("age")>30 and indi.get("death")==None and indi.get("fams")==None):
            temp_list.append(indi.get("id"))
    print "List of living, single people over 30 who haven't been married: " + ', '.join(temp_list)

def print_list_deceased():
    temp_list = []
    for indi in indiList:
        if(indi.get("death")):
            temp_list.append(indi.get("id"))
    print "List of deceased people: " + ', '.join(temp_list)

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
