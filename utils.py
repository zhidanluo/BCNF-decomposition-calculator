def readFile(fileName):
    # read file
    with open(fileName, 'r') as f:
        data = f.read()
    
    # split into attributes and FDs
    data_split = data.split('\n')

    # remove all ''
    while '' in data_split:
        data_split.remove('')

    for i, j in enumerate(data_split):
        # data_split[i] = j.replace(' ', '')
        data_split[i] = ''.join(j.split())
    
    # seperate attributes and FDs
    FDs = []
    attributes = []
    for element in data_split:
        if '->' in element:
            FDs.append(element)
        else:
            attributes.append(element)
    
    attributes_split = list(attributes[0])

    return FDs, attributes_split


def seperateFDs(FDs):
    # seperate LHS & RHS
    leftHS = []
    rightHS = []

    for fd in FDs:
        index = fd.index('-')
        # if index < 2:
        leftHS.append(fd[:index])
        rightHS.append(fd[index+2:])

    return leftHS, rightHS


def findIndex(attr, lhs):

    index = []
    for sub_attr in attr:
        for i, element in enumerate(lhs):
            if element == sub_attr:
                index.append(i)

    return index


def addFD(f, add_attr):

    f_add = []
    items = list(add_attr)
    for item in items:
        if not item in f:
            f += item
            f_add.append(item)

    f_sort = ''.join(sorted(f))  

    return f_sort, f_add


def calculateFplus(fileName):

    FDs, attrs = readFile(fileName)
    
    lhs, rhs = seperateFDs(FDs)

    # begin to calculate F+ by attributes
    flag = []
    Fplus = []
    for attr in attrs:
        # f is F+ of a single attribute
        # initialize f by itself
        f = attr

        # flag store the index of attributes that need to be considered
        index = findIndex(attr, lhs)
        flag.extend(index)

        # add FD if flag is not empty
        while len(flag) != 0:
            # add first FD in flag if it can be added
            first_flag = flag[0]
            f, f_add = addFD(f, rhs[first_flag])

            # if f is updated, then flag also needs to update
            if len(f_add) != 0 :
                index = findIndex(f_add, lhs)
                flag.extend(index)

            # delete the index that has been considered
            flag.pop(0)
        # end while 
        Fplus.append(f)
    #end for

    relation = ''.join(attrs)
    return Fplus, relation
            

def check(Fs, relation, special = None):

    check_list = []
    if len(list(relation)) > 2:
        for i, F in enumerate(Fs):
            # super key or trivial or have just been broken
            if F == relation or len(F) == 1 or relation[i] == special:
                check_list.append(0)
            else:
                check_list.append(1)
    else:
        check_list.append(0)

    return check_list
                

def getBreakPoint(check_list, Fplus):

    index_list = [i for i, j in enumerate(check_list) if j == 1]
    length_list = [len(Fplus[index]) for index in index_list]
    index_break_point = index_list[length_list.index(max(length_list))]

    return index_break_point


def rest(rhs, relation):

    rhs_list = list(rhs)
    relation_list = list(relation)

    for element in rhs_list:
        relation_list.remove(element)

    left = ''.join(relation_list)

    return left


def update(Fplus, relation, sub_relation):

    F = []
    for i, attr in enumerate(list(relation)):
        if attr in list(sub_relation):
            f = list(Fplus[i])
            F_add = []
            for element in f:
                if element in list(sub_relation):
                    F_add.append(element)
            F_add = ''.join(F_add)
            F.append(F_add)

    return F


def calculateBCNF(fileName):

    Fplus, relation = calculateFplus(fileName)

    check_list = check(Fplus, relation)
    if sum(check_list) == 0:
        # print("The table is already in BCNF! No need to break down!")
        return list([relation])
    
    # flag stores tables that need to be broke
    flag = []
    flag.append([Fplus, relation])

    # tables in BCNF 
    solutions = []

    while len(flag) != 0:
        # break the first table stored in flag,  so update Fplus and relation
        Fplus = flag[0][0]
        relation = flag[0][1]
        check_list = check(Fplus, relation)

        # determine which attribute to break on
        index_break_point = getBreakPoint(check_list, Fplus)

        # calculate RHS & LHS + left
        rhs = Fplus[index_break_point]
        lhs = list(relation)[index_break_point]
        lhs = ''.join(sorted(lhs + rest(rhs, relation)))
        
        # update FD and relation of LHS and RHS
        F_right = update(Fplus, relation, rhs)
        F_left = update(Fplus, relation, lhs)

        break_point = list(relation)[index_break_point]
        rhs_check_list = check(F_right, rhs, break_point)
        lhs_check_list = check(F_left, lhs, break_point)

        if sum(rhs_check_list + lhs_check_list) == 0:
            solutions.append(rhs)
            solutions.append(lhs)
        elif sum(rhs_check_list) == 0 and sum(lhs_check_list) != 0:
            solutions.append(rhs)
            flag.append([F_left, lhs])
        elif sum(rhs_check_list) != 0 and sum(lhs_check_list) == 0:
            solutions.append(lhs)
            flag.append([F_right, rhs])
        else:
            flag.append([F_left, lhs])
            flag.append([F_right, rhs])

        # delete the relation that has been broken
        flag.pop(0)
    # end while

    return solutions


def printSol(file):
    FDs, attrs = readFile(file)
    sols = calculateBCNF(file)

    print("Processing file: %s" % file[file.rfind('/')+1:])
    print("R = (%s)." % (" ".join(attrs)))
    print("The functional dependencies are %s.\n" % (", ".join(FDs)))
    print("Decomposing R into tables in BCNF...")
    print("Result:\n%s\n\n" % (" // ".join(sols)))