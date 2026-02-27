def squares(a, b):
    for i in range(a, b + 1):
        yield i ** 2

a = int(input("Enter start number a: "))
b = int(input("Enter end number b: "))
for sq in squares(a, b):
    print(sq)