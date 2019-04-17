import database_helper as dh

def test_validateProduct(db):
    return db.validateProduct(1)

def test_validateBounderies(db):
    data = {
    "doc":7,
    "bom":7,
    "child":7
    }
    return db.validateBounderies(1,data)

def test_addProduct(db):
    product = {
        "cid":1,
        "meanDoc":3,
        "meanBom": 3,
        "meanChild": 3,
        "maxDoc": 6,
        "maxBom": 6,
        "maxChild": 6,
        "minDoc": 2,
        "minBom": 2,
        "minChild": 2,
        "nrComponents": 12
    }
    return db.addProduct(product)

def test_getProduct(db):
    return True#db.getProduct(1)

def test_validateComponentAmount(db):
    return db.validateComponentAmount(1,5)


def main():
    db = dh.database()
    print("addProduct():  " + str(test_addProduct(db)))
    print("\ngetProduct(): " + str(test_getProduct(db)))
    print("\nvalidateProduct(): " + str(test_validateProduct(db)))
    print("\nvalidateBounderies(): "+ str(test_validateBounderies(db)))
    print("\nvalidateComponentAmount(): "+str(test_validateComponentAmount(db)))

if __name__ == "__main__":
    main()
