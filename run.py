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
        for i, line in enumerate(f):
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
                entry = {"line": i+1}
            elif not entry:
                entry = {"line": i+1}
                
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
        US12_check_parents_age_valid()

        US31_print_list_single()
        US29_print_list_deceased()
        US30_print_list_living_married()
            
        print_indi_table()
        print_fam_table()

def add_entry(entry, type):
    if type == "INDI":
        if entry.get("birth"):
            if entry.get("death"):
                age = get_age(entry["birth"], entry["death"])
                if age < 0:
                    print "[Line {line}] US03 Error: INDI {id} has death date before birth date".format(**entry)
                else:
                    entry["age"] = age
            else:
                entry["age"] = get_age(entry["birth"], date.today())
        else:
            print "[Line {line}] Error: INDI {id} is missing a birth date".format(**entry)
        us07_maxAge150(entry)
        indiList.append(entry)
    if type == "FAM":
        us04_marrBeforeDiv(entry)
        if entry.get("marr") and entry.get("husb") and entry.get("wife"):
            husb = get_indi(entry['husb'])
            wif = get_indi(entry['wife'])
            us05_marrBeforeDeat(entry, husb, wif)
            us10_marrAfter14(entry, husb, wif)
            if husb.get("sex") != "M":
                print "[Line {line}] US21 Error: FAM {id} has husband that is not male".format(**entry)
            if wif.get("sex") != "F":
                print "[Line {line}] US21 Error: FAM {id} has wife that is not female".format(**entry)
        famList.append(entry)


def us04_marrBeforeDiv(entry):
    if entry.get("div") and entry.get("marr") and (get_age(entry.get("marr"),entry.get("div")) < 0):
        print "[Line {line}] US04 Error: FAM {id} has marriage date after divorce date".format(**entry)


def us05_marrBeforeDeat(entry, husb, wif):
    if (husb.get("death") and get_age(entry.get("marr"),husb["death"]) < 0) or (wif.get("death") and get_age(entry.get("marr"),wif["death"]) < 0):
        print "[Line {line}] US05 Error: FAM {id} has marriage after death date of one of the spouses".format(**entry)


def us07_maxAge150(entry):
    # if (entry.get("death") and (get_age(entry.get("birth"),entry.get("death")) > 150)) or (get_age(entry.get("birth"),date.today()) > 150): worked but overly complex
    if entry.get("age") > 150:
        print "[Line {line}] US07 Error: INDI {id} {name} is claimed to be over 150 years old".format(**entry)


def us10_marrAfter14(entry,husb,wif):
    if (get_age(husb.get("birth"),entry.get("marr")) < 14) and (get_age(wif.get("birth"),entry.get("marr")) < 14):
        print "[Line {line}] US10 Error: FAM {id} marriage occurred prior to 14th birthdays of husband and wife".format(**entry)
    elif get_age(husb.get("birth"),entry.get("marr")) < 14:
        print "[Line {line}] US10 Error: FAM {id} marriage occurred prior to 14th birthday of husband".format(**entry)
    elif get_age(wif.get("birth"),entry.get("marr")) < 14:
        print "[Line {line}] US10 Error: FAM {id} marriage occurred prior to 14th birthday of wife".format(**entry)

def US12_check_parents_age_valid():
    for fam in famList:
        if fam.get("children"):
            childIdList = fam.get("children")
            fatherId = fam.get("husb")
            motherId = fam.get("wife")
            father = get_indi(fatherId)
            mother = get_indi(motherId)
            for childId in childIdList:
                child = get_indi(childId)
                if mother.get("age") and child.get("age") and mother["age"] - child["age"] >= 60:
                    print "[Line {line}] US12 Error: INDI's {id} Mother is 60 years or older than him/her".format(**child)
                if father.get("age") and child.get("age") and father["age"] - child["age"] >= 80:
                    print "[Line {line}] US12 Error: INDI's {id} Father is 80 years or older than him/her".format(**child)

def check_birth_before_marr():
    for entry in indiList:
        famIdList = entry.get("fams")
        if famIdList:
            for famId in famIdList:
                fam = get_fam(famId)
                if get_age(entry["birth"], fam["marr"]) < 0:
                    print "[Line {line}] US02 Error: INDI {id} has marriage date before birth date".format(**entry)

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

    # print "<-- {}|{}|{}|{}".format(**level,tag,valid,arguments)
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
    print "Individuals\n", t
                  
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

def US29_print_list_deceased():
    list_of_deceased = get_list('deceased')
    if list_of_deceased:
        print "(US29) List of deceased people: " + ', '.join(list_of_deceased)
    else:
        print "(US29) There are no deceased individuals"

def US30_print_list_living_married():
    list_of_married = get_list('married')
    if list_of_married:
        print "(US30) List of living, married people: " + ', '.join(list_of_married)
    else:
        print "(US30) There are no living, married individuals"

def US31_print_list_single():
    list_of_singles = get_list('single')
    if list_of_singles:
        print "(US31) List of living, single people over 30 who have never been married: " + ', '.join(list_of_singles)
    else:
        print "(US31) There are no living, single people over 30"

def get_list(type):
    list_of_people = []
    if type == 'single':
        for indi in indiList:
            if indi.get("age") > 30 and indi.get("death") is None and indi.get("fams") is None:
                id_and_name = indi.get("id") + " " + indi.get("name")
                list_of_people.append(id_and_name)
    elif type == 'deceased':
        for indi in indiList:
            if indi.get("death"):
                id_and_name = indi.get("id") + " " + indi.get("name")
                list_of_people.append(id_and_name)
    elif type == 'married':
        for fam in famList:
            husb = get_indi(fam['husb'])
            wife = get_indi(fam['wife'])
            if husb.get("death") is None and wife.get("death") is None and fam.get("div") is None:
                id_name_husb = husb.get("id") + " " + husb.get("name")
                id_name_wife = wife.get("id") + " " + wife.get("name")
                list_of_people.append(id_name_husb)
                list_of_people.append(id_name_wife)
    return list_of_people

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
