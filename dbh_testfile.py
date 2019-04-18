import database_helper as dh

def test_validateComponent(db):
    return db.validateComponent(1)

def test_validateBounderies(db):
    data = {
    "totaldocs":7,
    "BOMitems":7,
    "nrofchildren":7
    }
    return db.validateBounderies(1,data)

def test_addComponent(db):
    Component = {
        "cid":3,
        "MeanDocuments":3,
        "MeanBOMItem": 3,
        "MeanLeaves": 3,
        "MaxDocuments": 6,
        "MaxBOMItem": 6,
        "MaxLeaves": 6,
        "MinDocuments": 2,
        "MinBOMItem": 2,
        "MinLeaves": 2,
        "TotalComponents": 12
    }
    return db.addComponent(Component)

def test_getComponent(db):
    return True#db.getComponent(1)

def test_validateComponentAmount(db):
    return db.validateComponentAmount(1,5)


def main():
    db = dh.database()
    print("addComponent():  " + str(test_addComponent(db)))
    print("\ngetComponent(): " + str(test_getComponent(db)))
    print("\nvalidateComponent(): " + str(test_validateComponent(db)))
    print("\nvalidateBounderies(): "+ str(test_validateBounderies(db)))
    print("\nvalidateComponentAmount(): "+str(test_validateComponentAmount(db)))

if __name__ == "__main__":
    main()
