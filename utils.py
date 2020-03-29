import _config
import os

inputFileFolder = _config.inputFileFolder
save = _config.save
printf = _config.printf
printFplus = _config.printFplus


def preprocess(fileName):
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

    return data_split


def readFile(fileName):

    data = preprocess(fileName)
    
    # seperate attributes and FDs
    FDs = []
    attributes = []
    for element in data:
        if '->' in element:
            FDs.append(element)
        else:
            attributes.append(element)

    return FDs, attributes


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

    FDs, attributes = readFile(fileName)
    attrs = list(attributes[0])
    
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

    multiAttr = []
    for element in lhs:
        if element not in attrs:
            multiAttr.append(element)

    multiFplus = []
    for attr_list in multiAttr:
        f = attr_list
        consider = list(attr_list)
        consider.extend(list(rhs[lhs.index(attr_list)]))

        for attr in consider:
            f_to_add = Fplus[attrs.index(attr)]
            f, _ = addFD(f, f_to_add)
        
        multiFplus.append(f)

    relation = ''.join(attrs)

    return Fplus, relation, multiFplus, multiAttr
            

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

    Fplus, relation, _, _ = calculateFplus(fileName)

    check_list = check(Fplus, relation)
    if sum(check_list) == 0:

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


def solve(file, printInfo):

    FDs, attributes = readFile(file)
    attrs = list(attributes[0])
    
    sols = calculateBCNF(file)

    printf = printInfo[0]
    printFplus = printInfo[1]
    if printf:
        print("================================================================\n")
        print("Processing file: %s" % file[file.rfind('/')+1:])
        print("R = (%s)." % (" ".join(attrs)))
        print("The functional dependencies are %s." % (", ".join(FDs)))

        if printFplus:
            showFplus(file)

        if len(sols) == 1:
            print("\nR is already in BCNF! No need to break down!\n")
        else:
            print("\nDecomposing R into tables in BCNF...")
            print("Result:\n%s\n" % (" // ".join(sols)))

    return sols


def saveSol(file, sols):
    # save file
    with open("./output/" + file, 'w') as f:
        f.write(" // ".join(sols))

    print("Successfully saved solutions to '%s'!\n" % file)


def showFplus(file):

    Fplus, relation, multiFplus, multiAttr = calculateFplus(file)

    Fplus.extend(multiFplus)
    attrs = list(relation)
    attrs.extend(multiAttr)
    
    print("\nF+:")
    for i, attr in enumerate(attrs):
        print("%s -> %s" % (attr, Fplus[i]))


def checkFile(fileName):

    if fileName[-4:] != '.txt':
        print("Nonvalid input '%s': not a txt file!" % fileName)
        os._exit(0)

    FDs, attributes = readFile(inputFileFolder + fileName)
    # check wether to have FD or not
    if len(FDs) == 0:
        print("Nonvalid input '%s': no FDs found!" % fileName)
        os._exit(0)
    # check wether number of relation definition is 1 
    elif len(attributes) != 1:
        print("Nonvalid input '%s': definition error in relation!" % fileName)
        os._exit(0)

    leftHS, rightHS = seperateFDs(FDs)
    # check wether both LHS & RHS have attribute defined like '->bc' or 'a->'
    if '' in leftHS or '' in rightHS:
        print("Nonvalid input '%s': definition error in FD!" % fileName)
        os._exit(0)  

    # check wether have unkown attribute or character defined in FD like 'a->b@c'
    for fd in FDs:
        fd = fd.replace('->', '', 1)
        for i in list(fd):
            if i not in list(attributes[0]):
                print("Nonvalid input '%s': unkown attribute '%s'!" % (fileName, i))
                os._exit(0)

    check_list = leftHS + rightHS
    # check wether have repetition attributes defined in a single FD like 'a->bcc'
    for item in check_list:
        item_list = list(item)
        for i in item_list:
            if item_list.count(i) != 1:
                print("Nonvalid input '%s': definition error in '%s'!" % (fileName, item))
                os._exit(0)
        

def BCNF(file):

    fileName = inputFileFolder + file
    sols = solve(fileName, [printf, printFplus])
    if save:
        saveFileName = "Sol_" + file
        saveSol(saveFileName, sols)
