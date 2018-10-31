import unittest
import sys
from contextlib import contextmanager
from StringIO import StringIO
from datetime import date
import run

@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr
    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err

run.main("testfile.ged")

# Birth before marriage
class US02Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []
        
    def test_no_birth(self):
        entry = {"line": 1, "id": "i01"}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
            run.check_birth_before_marr()
        output = out.getvalue().strip()
        self.assertIn("INDI i01 is missing a birth date", output)
    
    def test_no_marr(self):
        entry = {"line": 2, "id": "i02", "birth": date.today()}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
            run.check_birth_before_marr()
        output = out.getvalue().strip()
        self.assertEquals("", output)
    
    def test_birth_before_marr(self):
        entry = {"line": 3, "id": "i03", "birth": date(1992,5,23), "fams": ["f01"]}
        famEntry = {"line": 4, "id": "f01", "marr": date(2017,3,4)}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
            run.add_entry(famEntry, "FAM")
            run.check_birth_before_marr()
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
    def test_marr_before_birth(self):
        entry = {"line": 5, "id": "i04", "birth": date(1998,3,25), "fams": ["f02"]}
        famEntry = {"line": 6, "id": "f02", "marr": date(1993,4,6)}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
            run.add_entry(famEntry, "FAM")
            run.check_birth_before_marr()
        output = out.getvalue().strip()
        self.assertIn("INDI i04 has marriage date before birth date", output)
        
    def test_birth_marr_same(self):
        entry = {"line": 7, "id": "i05", "birth": date.today(), "fams": ["f03"]}
        famEntry = {"line": 8, "id": "f03", "marr": date.today()}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
            run.add_entry(famEntry, "FAM")
            run.check_birth_before_marr()
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
# Birth before death
class US03Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []
        
    def test_birth_before_death(self):
        entry = {"line": 0, "id": "i01", "birth": date(1992,5,23), "death": date(2017,3,4)}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
    def test_death_before_birth(self):
        entry = {"line": 1, "id": "i02", "birth": date(1998,3,25), "death": date(1993,4,6)}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertIn("INDI i02 has death date before birth date", output)
        
    def test_birth_death_same(self):
        entry = {"line": 2, "id": "i05", "birth": date.today(), "death": date.today()}
        with captured_output() as (out,err):
            run.add_entry(entry, "INDI")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
# Marriage before divorce
class US04Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []
        
    def test_no_div(self):
        entry = {"line": 1, "id": "f01", "name":"test", "marr": date(1992,5,23)}
        with captured_output() as (out,err):
            run.add_entry(entry, "FAM")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
    def test_marr_before_div(self):
        entry = {"line": 2, "id": "f01", "name":"test", "marr": date(1992,5,23), "div": date(2017,3,4)}
        with captured_output() as (out,err):
            run.add_entry(entry, "FAM")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
    def test_div_before_marr(self):
        entry = {"line": 3, "id": "f02", "name":"test", "marr": date(1998,3,25), "div": date(1993,4,6)}
        with captured_output() as (out,err):
            run.add_entry(entry, "FAM")
        output = out.getvalue().strip()
        self.assertIn("[Line 3] US04 Error: FAM f02 has marriage date after divorce date", output)
        
    def test_marr_div_same(self):
        entry = {"line": 4, "id": "f03", "name":"test", "marr": date.today(), "div": date.today()}
        with captured_output() as (out,err):
            run.add_entry(entry, "FAM")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
# Marriage before death
class US05Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []
        
    def test_marr_no_death(self):
        husb_entry = {"line": 1, "id": "i01", "name":"test", "birth": date(1980,5,20), "fams": ["f01"], "sex": "M"}
        wife_entry = {"line": 2, "id": "i02", "name":"test", "birth": date(1982,6,10), "fams": ["f01"], "sex": "F"}
        fam_entry = {"line": 3, "id": "f01", "husb": "i01", "wife": "i02", "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
    def test_marr_before_death(self):
        husb_entry = {"line": 4, "id": "i03", "name":"test", "birth": date(1980,5,20), "death": date(2017,3,4), "fams": ["f02"], "sex": "M"}
        wife_entry = {"line": 5, "id": "i04", "name":"test", "birth": date(1982,6,10), "death": date(2017,3,4), "fams": ["f02"], "sex": "F"}
        fam_entry = {"line": 6, "id": "f02", "husb": "i03", "wife": "i04", "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
    def test_husb_death_before_marr(self):
        husb_entry = {"line": 7, "id": "i05", "name":"test", "birth": date(1980,5,20), "death": date(1999,3,4), "fams": ["f03"], "sex": "M"}
        wife_entry = {"line": 8, "id": "i06", "name":"test", "birth": date(1982,6,10), "death": date(2017,3,4), "fams": ["f03"], "sex": "F"}
        fam_entry = {"line": 9, "id": "f03", "husb": "i05", "wife": "i06", "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
        output = out.getvalue().strip()
        self.assertIn("FAM f03 has marriage after death date of one of the spouses", output)
        
    def test_wife_death_before_marr(self):
        husb_entry = {"line": 10, "id": "i07", "name":"test", "birth": date(1980,5,20), "death": date(2017,3,4), "fams": ["f04"], "sex": "M"}
        wife_entry = {"line": 11, "id": "i08", "name":"test", "birth": date(1982,6,10), "death": date(1999,3,4), "fams": ["f04"], "sex": "F"}
        fam_entry = {"line": 12, "id": "f04", "husb": "i07", "wife": "i08", "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
        output = out.getvalue().strip()
        self.assertIn("FAM f04 has marriage after death date of one of the spouses", output)    
        
    def test_both_death_before_marr(self):
        husb_entry = {"line": 13, "id": "i09", "name":"test", "birth": date(1980,5,20), "death": date(1999,3,4), "fams": ["f05"], "sex": "M"}
        wife_entry = {"line": 14, "id": "i10", "name":"test", "birth": date(1982,6,10), "death": date(1999,3,4), "fams": ["f05"], "sex": "F"}
        fam_entry = {"line": 15, "id": "f05", "husb": "i09", "wife": "i10", "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
        output = out.getvalue().strip()
        self.assertIn("FAM f05 has marriage after death date of one of the spouses", output)

# Parents not too old
class US12Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []
        
    def test_normal_age(self):
        husb_entry = {"line": 1, "id": "i01", "birth": date(1980,5,20), "fams": ["f01"], "sex": "M"}
        wife_entry = {"line": 2, "id": "i02", "birth": date(1982,6,10), "fams": ["f01"], "sex": "F"}
        child_entry = {"line": 3, "id": "i03", "birth": date(2010,1,1), "famc": "f01"}
        fam_entry = {"line": 4, "id": "f01", "husb": "i01", "wife": "i02", "children": ["i03"], "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(child_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
            run.US12_check_parents_age_valid()
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
    def test_both_old(self):
        husb_entry = {"line": 5, "id": "i04", "birth": date(1925,5,20), "fams": ["f02"], "sex": "M"}
        wife_entry = {"line": 6, "id": "i05", "birth": date(1945,6,10), "fams": ["f02"], "sex": "F"}
        child_entry = {"line": 7, "id": "i06", "birth": date(2010,1,1), "famc": "f02"}
        fam_entry = {"line": 8, "id": "f02", "husb": "i04", "wife": "i05", "children": ["i06"], "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(child_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
            run.US12_check_parents_age_valid()
        output = out.getvalue().strip()
        self.assertIn("INDI's i06 Mother is 60 years or older than him/her", output)
        self.assertIn("INDI's i06 Father is 80 years or older than him/her", output)
        
    def test_husb_old(self):
        husb_entry = {"line": 9, "id": "i07", "birth": date(1925,5,20), "fams": ["f03"], "sex": "M"}
        wife_entry = {"line": 10, "id": "i08", "birth": date(1982,6,10), "fams": ["f03"], "sex": "F"}
        child_entry = {"line": 11, "id": "i09", "birth": date(2010,1,1), "famc": "f03"}
        fam_entry = {"line": 12, "id": "f03", "husb": "i07", "wife": "i08", "children": ["i09"], "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(child_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
            run.US12_check_parents_age_valid()
        output = out.getvalue().strip()
        self.assertIn("INDI's i09 Father is 80 years or older than him/her", output)
        
    def test_wife_old(self):
        husb_entry = {"line": 13, "id": "i10", "birth": date(1980,5,20), "fams": ["f04"], "sex": "M"}
        wife_entry = {"line": 14, "id": "i11", "birth": date(1945,6,10), "fams": ["f04"], "sex": "F"}
        child_entry = {"line": 15, "id": "i12", "birth": date(2010,1,1), "famc": "f04"}
        fam_entry = {"line": 16, "id": "f04", "husb": "i10", "wife": "i11", "children": ["i12"], "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(child_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
            run.US12_check_parents_age_valid()
        output = out.getvalue().strip()
        self.assertIn("INDI's i12 Mother is 60 years or older than him/her", output)
        
# List Deceased
class US29Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []

    def test_list_single(self):
        entry1 = {"id": "i01", "name": "John /Smith/", "birth": date(1986, 9, 9), "sex": "M"}
        entry2 = {"id": "i02", "name": "Kevin /Anderson/", "birth": date(1999, 9, 9), "sex": "M"}
        entry3 = {"id": "i03", "name": "Connor /Thompson/", "birth": date(1939, 2, 23), "sex": "M", "fams": ["f01"], "death": date(2014, 3, 2)}
        entry4 = {"id": "i04", "name": "Wendy /Anderson/", "birth": date(2009, 11, 30), "sex": "F", "death": date(2015, 3, 2)}
        entry5 = {"id": "i05", "name": "Danielle /Jones/", "birth": date(1950, 1, 13), "sex": "F"}
        with captured_output() as (out, err):
            run.add_entry(entry1, "INDI")
            run.add_entry(entry2, "INDI")
            run.add_entry(entry3, "INDI")
            run.add_entry(entry4, "INDI")
            run.add_entry(entry5, "INDI")
            run.US29_print_list_deceased()
        output = out.getvalue().strip()
        self.assertEquals("(US29) List of deceased people: i03 Connor /Thompson/, i04 Wendy /Anderson/", output)

# List Married
class US30Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []

    def test_list_married_both_alive(self):
        husb_entry = {"id": "i05", "name": "John /Smith/", "birth": date(1980,5,20), "fams": ["f03"], "sex": "M"}
        wife_entry = {"id": "i06", "name": "Wendy /Anderson/", "birth": date(1982,6,10), "fams": ["f03"], "sex": "F"}
        fam_entry = {"id": "f03", "husb": "i05", "wife": "i06", "marr": date(1998,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
            run.US30_print_list_living_married()
        output = out.getvalue().strip()
        self.assertEquals("(US30) List of living, married people: i05 John /Smith/, i06 Wendy /Anderson/", output)

    def test_list_married_husb_dead(self):
        husb_entry = {"id": "i05", "name": "John /Smith/", "birth": date(1980,5,20), "death": date(1999,3,4), "fams": ["f03"], "sex": "M"}
        wife_entry = {"id": "i06", "name": "Wendy /Anderson/", "birth": date(1982,6,10), "fams": ["f03"], "sex": "F"}
        fam_entry = {"id": "f03", "husb": "i05", "wife": "i06", "marr": date(1998,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
            run.US30_print_list_living_married()
        output = out.getvalue().strip()
        self.assertEquals("(US30) There are no living, married individuals", output)

    def test_list_married_divorce(self):
        husb_entry = {"id": "i05", "name": "John /Smith/", "birth": date(1980,5,20), "death": date(1999,3,4), "fams": ["f03"], "sex": "M"}
        wife_entry = {"id": "i06", "name": "Wendy /Anderson/", "birth": date(1982,6,10), "fams": ["f03"], "sex": "F"}
        fam_entry = {"id": "f03", "husb": "i05", "wife": "i06", "marr": date(1998,6,20), "div": date(1999,3,4)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
            run.US30_print_list_living_married()
        output = out.getvalue().strip()
        self.assertEquals("(US30) There are no living, married individuals", output)

# List living single
class US31Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []

    def test_list_single(self):
        entry1 = {"id": "i01", "name": "John /Smith/", "birth": date(1986, 9, 9), "sex": "M"}
        entry2 = {"id": "i02", "name": "Kevin /Anderson/", "birth": date(1999, 9, 9), "sex": "M"}
        entry3 = {"id": "i03", "name": "Connor /Thompson/", "birth": date(1939, 2, 23), "sex": "M", "fams": ["f01"]}
        entry4 = {"id": "i04", "name": "Wendy /Anderson/", "birth": date(2009, 11, 30), "sex": "F", "death": date(2015, 3, 2)}
        entry5 = {"id": "i05", "name": "Danielle /Jones/", "birth": date(1950, 1, 13), "sex": "F"}
        with captured_output() as (out, err):
            run.add_entry(entry1, "INDI")
            run.add_entry(entry2, "INDI")
            run.add_entry(entry3, "INDI")
            run.add_entry(entry4, "INDI")
            run.add_entry(entry5, "INDI")
            run.US31_print_list_single()
        output = out.getvalue().strip()
        self.assertEquals("(US31) List of living, single people over 30 who have never been married: i01 John /Smith/, i05 Danielle /Jones/", output)

# List recent births
class US35Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []

    def test_list_single(self):
        entry1 = {"id": "i01", "name": "John /Smith/", "birth": date(2018, 10, 20), "sex": "M"}
        entry3 = {"id": "i03", "name": "Connor /Thompson/", "birth": date(1939, 2, 23), "sex": "M", "fams": ["f01"]}
        entry4 = {"id": "i04", "name": "Wendy /Anderson/", "birth": date(2018, 9, 23), "sex": "F"}
        entry5 = {"id": "i05", "name": "Danielle /Jones/", "birth": date(2018, 10, 24), "sex": "F"}
        with captured_output() as (out, err):
            run.add_entry(entry1, "INDI")
            run.add_entry(entry3, "INDI")
            run.add_entry(entry4, "INDI")
            run.add_entry(entry5, "INDI")
            run.US35_list_recent_birth()
        output = out.getvalue().strip()
        self.assertEquals("(US35) List of people that were born in the last 30 days: i01 John /Smith/, i05 Danielle /Jones/", output)

# List recent deaths
class US36Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []

    def test_list_single(self):
        entry1 = {"id": "i01", "name": "John /Smith/", "birth": date(1990, 10, 20), "sex": "M", "death": date(2018, 10, 20)}
        entry3 = {"id": "i03", "name": "Connor /Thompson/", "birth": date(1939, 2, 23), "sex": "M", "fams": ["f01"]}
        entry4 = {"id": "i04", "name": "Wendy /Anderson/", "birth": date(1950, 9, 23), "sex": "F"}
        entry5 = {"id": "i05", "name": "Danielle /Jones/", "birth": date(1960, 10, 24), "sex": "F", "death": date(2018, 9, 28)}
        with captured_output() as (out, err):
            run.add_entry(entry1, "INDI")
            run.add_entry(entry3, "INDI")
            run.add_entry(entry4, "INDI")
            run.add_entry(entry5, "INDI")
            run.US36_list_recent_deaths()
        output = out.getvalue().strip()
        self.assertEquals("(US36) List of people that died in the last 30 days: i01 John /Smith/, i05 Danielle /Jones/", output)
   
# Correct gender for role
class US21Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []
        
    def test_both_correct(self):
        husb_entry = {"line": 1, "id": "i01", "birth": date(1980,5,20), "fams": ["f01"], "sex": "M"}
        wife_entry = {"line": 2, "id": "i02", "birth": date(1982,6,10), "fams": ["f01"], "sex": "F"}
        fam_entry = {"line": 3, "id": "f01", "husb": "i01", "wife": "i02", "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
        output = out.getvalue().strip()
        self.assertEquals("", output)
        
    def test_husb_not_male(self):
        husb_entry = {"line": 4, "id": "i03", "birth": date(1980,5,20), "death": date(2017,3,4), "fams": ["f02"], "sex": "F"}
        wife_entry = {"line": 5, "id": "i04", "birth": date(1982,6,10), "death": date(2017,3,4), "fams": ["f02"], "sex": "F"}
        fam_entry = {"line": 6, "id": "f02", "husb": "i03", "wife": "i04", "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
        output = out.getvalue().strip()
        self.assertIn("FAM f02 has husband that is not male", output)
        
    def test_wife_not_female(self):
        husb_entry = {"line": 7, "id": "i05", "birth": date(1980,5,20), "death": date(2018,3,4), "fams": ["f03"], "sex": "M"}
        wife_entry = {"line": 8, "id": "i06", "birth": date(1982,6,10), "death": date(2017,3,4), "fams": ["f03"], "sex": "M"}
        fam_entry = {"line": 9, "id": "f03", "husb": "i05", "wife": "i06", "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
        output = out.getvalue().strip()
        self.assertIn("FAM f03 has wife that is not female", output)
        
    def test_both_incorrect(self):
        husb_entry = {"line": 10, "id": "i07", "birth": date(1980,5,20), "death": date(2017,3,4), "fams": ["f04"], "sex": "F"}
        wife_entry = {"line": 11, "id": "i08", "birth": date(1982,6,10), "death": date(2017,3,4), "fams": ["f04"], "sex": "M"}
        fam_entry = {"line": 12, "id": "f04", "husb": "i07", "wife": "i08", "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
        output = out.getvalue().strip()
        self.assertIn("FAM f04 has husband that is not male", output)
        self.assertIn("FAM f04 has wife that is not female", output)  
        
# Include input line numbers
class US40Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []
        
    def test_line_errors(self):
        husb_entry = {"line": 1, "id": "i07", "birth": date(1980,5,20), "death": date(1977,3,4), "fams": ["f04"], "sex": "F"}
        wife_entry = {"line": 2, "id": "i08", "birth": date(1982,6,10), "death": date(2017,3,4), "fams": ["f04"], "sex": "F"}
        fam_entry = {"line": 3, "id": "f04", "husb": "i07", "wife": "i08", "marr": date(2000,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
        output = out.getvalue().strip()
        self.assertEquals("[Line 1] US03 Error: INDI i07 has death date before birth date\n[Line 3] US05 Error: FAM f04 has marriage after death date of one of the spouses\n[Line 3] US21 Error: FAM f04 has husband that is not male", output)


# Include input line numbers
class US07Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []

    def test_line_errors(self):
        ent = {"line": 1, "id": "i01", "name":"test", "birth": date(1901,1,10), "death": date(2070,1,1), "fams": ["f01"], "sex": "F"}
        with captured_output() as (out,err):
            run.add_entry(ent, "INDI")
        output = out.getvalue().strip()
        self.assertEquals("[Line 1] US07 Error: INDI i01 test is claimed to be over 150 years old", output)


# Include input line numbers
class US10Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []

    def test_both(self):
        husb = {"line": 1, "id": "i01", "name":"husband", "birth": date(2001,12,10), "fams": ["f01"], "sex": "M"}
        wif = {"line": 10, "id": "i02", "name":"wife", "birth": date(2000,1,10), "fams": ["f01"], "sex": "F"}
        fam = {"line": 30, "id": "f01", "husb": "i01", "wife": "i02", "marr": date(2010,1,10)}
        with captured_output() as (out,err):
            run.add_entry(husb, "INDI")
            run.add_entry(wif, "INDI")
            run.add_entry(fam, "FAM")
        output = out.getvalue().strip()
        self.assertEquals("[Line 30] US10 Error: FAM f01 marriage occurred prior to 14th birthdays of husband and wife", output)

    def test_husb(self):
        husb = {"line": 1, "id": "i01", "name":"husband", "birth": date(2001,12,10), "fams": ["f01"], "sex": "M"}
        wif = {"line": 10, "id": "i02", "name":"wife", "birth": date(1901,1,10), "fams": ["f01"], "sex": "F"}
        fam = {"line": 30, "id": "f01", "husb": "i01", "wife": "i02", "marr": date(2010,1,10)}
        with captured_output() as (out,err):
            run.add_entry(husb, "INDI")
            run.add_entry(wif, "INDI")
            run.add_entry(fam, "FAM")
        output = out.getvalue().strip()
        self.assertEquals("[Line 30] US10 Error: FAM f01 marriage occurred prior to 14th birthday of husband", output)

    def test_wif(self):
        husb = {"line": 1, "id": "i01", "name":"husband", "birth": date(1901,12,10), "fams": ["f01"], "sex": "M"}
        wif = {"line": 10, "id": "i02", "name":"wife", "birth": date(2000,1,10), "fams": ["f01"], "sex": "F"}
        fam = {"line": 30, "id": "f01", "husb": "i01", "wife": "i02", "marr": date(2010,1,10)}
        with captured_output() as (out,err):
            run.add_entry(husb, "INDI")
            run.add_entry(wif, "INDI")
            run.add_entry(fam, "FAM")
        output = out.getvalue().strip()
        self.assertEquals("[Line 30] US10 Error: FAM f01 marriage occurred prior to 14th birthday of wife", output)
        
# List Orphans
class US33Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []

    def test_list_orphans_both_alive(self):
        husb_entry = {"id": "i01", "name": "John /Smith/", "birth": date(1980,5,20), "fams": ["f01"], "sex": "M"}
        wife_entry = {"id": "i02", "name": "Wendy /Anderson/", "birth": date(1982,6,10), "fams": ["f01"], "sex": "F"}
        child_entry = {"id": "i03", "name": "Bob /Smith/", "birth": date(2005,3,10), "famc": "f01", "sex": "M"}
        child2_entry = {"id": "i04", "name": "Bobolder /Smith/", "birth": date(1999,3,10), "famc": "f01", "sex": "M"}
        fam_entry = {"id": "f01", "husb": "i01", "wife": "i02", "children": ["i03","i04"], "marr": date(1998,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(child_entry, "INDI")
            run.add_entry(child2_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
            run.US33_print_list_orphans()
        output = out.getvalue().strip()
        self.assertEquals("(US33) There are no orphans", output)

    def test_list_orphans_both_dead(self):
        husb_entry = {"id": "i01", "name": "John /Smith/", "birth": date(1980,5,20), "death": date(2018,3,11), "fams": ["f01"], "sex": "M"}
        wife_entry = {"id": "i02", "name": "Wendy /Anderson/", "birth": date(1982,6,10), "death": date(2018,3,11), "fams": ["f01"], "sex": "F"}
        child_entry = {"id": "i03", "name": "Bob /Smith/", "birth": date(2005,3,10), "famc": "f01", "sex": "M"}
        child2_entry = {"id": "i04", "name": "Bobolder /Smith/", "birth": date(1999,3,10), "famc": "f01", "sex": "M"}
        fam_entry = {"id": "f01", "husb": "i01", "wife": "i02", "children": ["i03","i04"], "marr": date(1998,6,20)}
        with captured_output() as (out,err):
            run.add_entry(husb_entry, "INDI")
            run.add_entry(wife_entry, "INDI")
            run.add_entry(child_entry, "INDI")
            run.add_entry(child2_entry, "INDI")
            run.add_entry(fam_entry, "FAM")
            run.US33_print_list_orphans()
        output = out.getvalue().strip()
        self.assertEquals("(US33) List of orphans: i03 Bob /Smith/", output)
        
# Include individual ages
class US27Test(unittest.TestCase):
    def setUp(self):
        run.indiList = []
        run.famList = []

    def test_ages(self):
        entry1 = {"id": "i01", "name": "John /Smith/", "birth": date(1980,5,20), "death": date(2005,2,3), "fams": ["f01"], "sex": "M"}
        entry2 = {"id": "i02", "name": "Wendy /Anderson/", "birth": date(1982,6,10), "death": date(2003,8,12), "fams": ["f01"], "sex": "F"}
        entry3 = {"id": "i03", "name": "Bob /Anderson/", "birth": date(1990,6,10), "fams": ["f01"], "sex": "F"}
        with captured_output() as (out,err):
            run.add_entry(entry1, "INDI")
            run.add_entry(entry2, "INDI")
            run.add_entry(entry3, "INDI")
        output = out.getvalue().strip()
        self.assertEquals(run.get_indi("i01").get("age"), 24)
        self.assertEquals(run.get_indi("i02").get("age"), 21)
        self.assertEquals(run.get_indi("i03").get("age"), 28)


unittest.main()