# First match example
a = 2
match a:
    case 1:
        print("True")
    case 2:
        print("False")

# Second match example with if-else
b = 4
d = 3

if (b + d) == 7:
    a = 1
    match a:
        case 1:
            print("True")
        case 2:
            print("False")
else:
    a = 2
    match a:
        case 1:
            print("True")
        case 2:
            print("False")
