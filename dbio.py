from collections import namedtuple

ENGLISH_TAG = ('英语', '单词', '听力', '口语', '四级', '六级', '托福', 'TOEFL', 'Toefl', 'toefl', 
                '雅思', 'eng', 'Eng', 'FET', 'fet', 'Fet', 'cet', 'Cet', 'CET')
MATH_TAG = ('数学', 'math', 'Math', '数分', '高数', '离散', '线代', '高代', '代数', '几何', '逻辑')
ENTERTAINMENT_TAG = ('看剧', '追剧', '电影', '影视')


ToDo = namedtuple('ToDo', ['lN', 'isFinished', 'remark'])

def create(uid: any) -> int:
    try:
        with open(f'./data/{str(uid)}.db', 'a', encoding='utf8') as f:
            pass
        return 0
    except Exception as e:
        print(f'Error when creating a database for {str(uid)}: {e}')
        return 1

def readAll(uid: any) -> list[ToDo]:
    try:
        with open(f'./data/{str(uid)}.db', encoding='utf8') as f:
            lines = [each.strip() for each in f.readlines()]
        results = []
        for line in lines:
            if line.strip() != '':
                isFinished, remark = line.split(' ', 1)
                if isFinished == 'x':
                    isFinished = True
                elif isFinished == 'o':
                    isFinished = False
                lN = len(results)
                results.append(ToDo(lN, isFinished, remark.strip()))
        return results
    except Exception as e:
        print(f'Error when reading the database of {str(uid)}: {e}')
        return [-1]

def clearAll(uid: any) -> int:
    try:
        with open(f'./data/{str(uid)}.db', encoding='utf8') as f:
            pass
        with open(f'./data/{str(uid)}.db', 'w', encoding='utf8') as f:
            pass
        return 0
    except Exception as e:
        print(f'Error when clearing the database of {str(uid)}: {e}')
        return 1

def writeAll(uid: any, toDoList: list[ToDo]) -> int:
    try:
        db = []
        for toDo in toDoList:
            toDo: ToDo
            stat = 'x' if toDo.isFinished else 'o'
            db.append(f'{stat} {toDo.remark}')
        with open(f'./data/{str(uid)}.db', 'w', encoding='utf8') as f:
            print(*db, sep='\n', file=f)
        return 0
    except Exception as e:
        print(f'Error when writing the database of {str(uid)}: {e}')
        return 1


def classify(toDoList: list[ToDo]) -> dict:
    __doc__ = 'key: hashtag; value: [ToDo()]'
    try:
        result = {'Unclassified': []}
        assert not -1 in toDoList
        for toDo in toDoList:
            toDo: ToDo
            if toDo.remark.find('#') in (-1, len(toDo.remark)-1):
                result['Unclassified'].append(toDo)
            else:
                kw0 = toDo.remark
                while kw0.find('#') != -1:
                    kw = kw0[kw0.find('#')+1:]
                    if ' ' in kw0[kw0.find('#'):]:
                        kw = kw[:kw.find(' ')]
                    if kw in result.keys():
                        result[kw].append(toDo)
                    else:
                        result[kw] = [toDo]
                    kw0 = kw0[kw0.find('#')+1:]
        return result
    except Exception as e:
        print(f'Error when classifying a list: {e}')
        return dict()

def getToDo(uid: any, lN: any) -> ToDo:
    try:
        toDoList: list = readAll(uid)
        assert not -1 in toDoList
        for toDo in toDoList:
            if toDo.lN == int(lN):
                return toDo
        assert False
    except Exception as e:
        print(f'Error when reading a to-do for {str(uid)}: {e}')
        return ToDo('', False, '')

def addToDo(uid: any, remark: str) -> int:
    try:
        remark = remark.strip()
        if '&' in remark:
            r1, r2 = remark.split('&', 1)
            return addToDo(uid, r1) + addToDo(uid, r2)
        else:
            toDoList: list = readAll(uid)
            assert not -1 in toDoList
            for each in ENGLISH_TAG:
                if each in remark:
                    remark += ' #english'
                    break
            for each in MATH_TAG:
                if each in remark:
                    remark += ' #math'
                    break
            for each in ENTERTAINMENT_TAG:
                if each in remark:
                    remark += ' #entertainment'
                    break
            toDoList.append(ToDo('', False, remark))
            status = writeAll(uid, toDoList)
            return status
    except Exception as e:
        print(f'Error when adding a to-do for {str(uid)}: {e}')
        return 1

def delToDo(uid: any, lN: str) -> int:
    try:
        ls = [int(l.strip()) for l in lN.split('&')]
        toDoList: list = readAll(uid)
        newList = []
        assert not -1 in toDoList
        flag = False
        for toDo in toDoList:
            if not toDo.lN in ls:
                newList.append(toDo)
                flag = True
        assert flag
        writeAll(uid, newList)
        return 0
    except Exception as e:
        print(f'Error when deleting a to-do for {str(uid)}: {e}')
        return 1

def markToDo(uid: any, lN: any) -> any:
    try:
        if isinstance(lN, str) and '&' in lN:
            ls = lN.split('&')
            result = 0
            for each in ls:
                result += markToDo(uid, each)
        else:
            toDoList: list = readAll(uid)
            assert not -1 in toDoList
            flag = False
            for i, toDo in enumerate(toDoList):
                toDo: ToDo
                if toDo.lN == int(lN):
                    f = not toDo.isFinished
                    new = ToDo(toDo.lN, f, toDo.remark)
                    toDoList.pop(i)
                    toDoList.insert(i, new)
                    flag = True
                    break
            assert flag
            writeAll(uid, toDoList)
            return 0
    except Exception as e:
        print(f'Error when marking a to-do for {str(uid)}: {e}')
        return 1

def getTag(uid: any, tagname: any) -> list[ToDo]:
    try:
        toDoDict: dict = classify(readAll(uid))
        if str(tagname) in toDoDict.keys():
            return toDoDict[str(tagname)]
        else:
            return []
    except Exception as e:
        print(f'Error when reading a tag for {str(uid)}: {e}')
        return []
        

def completeAll(uid: any) -> int:
    try:
        toDoList = readAll(uid)
        newList = []
        assert not -1 in toDoList
        for toDo in toDoList:
            newList.append(ToDo(toDo.lN, True, toDo.remark))
        writeAll(uid, newList)
        return 0
    except Exception as e:
        print(f'Error when completing all to-dos for {str(uid)}: {e}')
        return 1