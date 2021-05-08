import sys

sys.path.append("../") # temp solution to my stupidity
cleanup = __import__("NoodleExtCleanup") # using __import__ because fucking errors
# this temp fix does prevent me from using the VScode built-in testing
# features but it's temp until I figure out a way to not have to
# constantly reinstall the package to test it


def testCleanup():
    pass

if __name__ == "__main__":
    print("\n"*10)
    cleanup.cleanup("./testLevel/ExpertPlusStandard.dat", "./testLevel/TestOutput.dat", ignore=False)
    print("\n"*10)
