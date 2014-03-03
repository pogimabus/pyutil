import unittest


class type_validator:
    """
    A function decorator, runs input through type validation before passing it on the the original function; returns
        False if the type does not match that which was expected (defined in dict 'types' class member variable)
        type_validator.types expected format: { func_name : expected_type }
    """
    def __init__(self, func):
        self.func = func
        self.types = type_validator.types

    def __call__(self, value):
        return self.func(value) and isinstance(value, self.types[self.func.func_code.co_name])


class Validator(object):
    """
    Validates values
    """
    def __init__(self, validation_funcs_dict, always_valid_types=None):
        """
        Initializes the object
        @type validation_funcs_dict: dict
        @param validation_funcs_dict: { func_name: function }
        @type always_valid_types: set or unknown
        @param always_valid_types: when a value's type is a member of this set, it always get evaluated as valid
        @return: self
        """
        self._validation_funcs_dict = validation_funcs_dict
        if always_valid_types is None:
            self.always_valid_types = set()
        else:
            self.always_valid_types = always_valid_types

    def is_valid(self, key, val):
        """
        Returns True if val is evaluated as valid, False otherwise
        @type key: str
        @param key: name of the function to use to validate val
        @type val: str or float or int or bool or list or unknown
        @param val: the value to validate
        @return: True if val is evaluated as valid, False otherwise
        """
        if type(val) in self.always_valid_types:
            return True
        try:
            return self._validation_funcs_dict[key](val)
        except KeyError:
            raise Validator.UndefinedKey("No validation function defined for '{}'".format(key))

    class UndefinedKey(Exception):
        pass


#--------------------
# Tests
#--------------------
class ValidationTests(unittest.TestCase):
    def setUp(self):
        type_validator.types = {"my_validator": float}

        @type_validator
        def my_validator(value):
            return value > 1

        self.type_validator_func = my_validator

    def test_type_validator(self):
        self.assertTrue(self.type_validator_func(1.1))
        self.assertFalse(self.type_validator_func(0.1))
        self.assertFalse(self.type_validator_func(1))

        # Validate the it still works if type_validator types changes
        type_validator.types = {}
        self.assertTrue(self.type_validator_func(1.1))


class ValidatorTests(unittest.TestCase):
    def setUp(self):
        self.validator = Validator({"x": lambda x: type(x) is int})

    def test_is_valid(self):
        self.assertTrue(self.validator.is_valid("x", 5))

    def test_is_valid_false(self):
        self.assertFalse(self.validator.is_valid("x", "5"))

    def test_is_valid_missing_key(self):
        self.assertRaises(Validator.UndefinedKey, self.validator.is_valid, "y", 5)