import unittest


def main():
    loader = unittest.TestLoader()
    suite = loader.discover('.', pattern='*.py')
    unittest.TextTestRunner().run(suite)


if __name__ == "__main__":
    main()
