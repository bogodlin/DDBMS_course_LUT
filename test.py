import unittest
from eye_for_eye.models import Case

def case_find():
    assert Case.query.filter_by(code='IT-PT-20201019-210608').first().id == 17, "Should be 17"

if __name__ == "__main__":
    case_find()
    print("Everything passed")