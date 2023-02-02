import os
from collections import namedtuple

ENGLISH_TAG = ('英语', '单词', '听力', '口语', '四级', '六级', '托福', 'TOEFL', 'Toefl', 'toefl', 
                '雅思', 'eng', 'Eng', 'FET', 'fet', 'Fet', 'cet', 'Cet', 'CET')
MATH_TAG = ('数学', 'math', 'Math', '数分', '高数', '离散', '线代', '高代', '代数', '几何', '逻辑')
ENTERTAINMENT_TAG = ('看剧', '追剧', '电影', '影视')


ToDo = namedtuple('ToDo', ['lN', 'isFinished', 'remark'])

def seekList(uid: any) -> list[str]:
    try:
        dbs = os.listdir('./data/')
        result = []
        for db in dbs:
            if db.startswith(str(uid)+'_'):
                result.append(db[db.find('_')+1:db.find('.db')])
        return result
    except Exception as e:
        print(f'Error when seeking lists of {str(uid)}: {e}')
        return []

def create(uid: any, listAlias: str='') -> int:
    try:
        filename = str(uid) if listAlias == '' else f'{str(uid)}_{listAlias}'
        with open(f'./data/{filename}.db', 'a', encoding='utf8') as f:
            pass
        return 0
    except Exception as e:
        print(f'Error when creating a database for {str(uid)}: {e}')
        return 1

def readAll(uid: any, listAlias: str='') -> list[ToDo]:
    try:
        filename = str(uid) if listAlias == '' else f'{str(uid)}_{listAlias}'
        with open(f'./data/{filename}.db', encoding='utf8') as f:
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

def clearAll(uid: any, listAlias: str='') -> int:
    try:
        filename = str(uid) if listAlias == '' else f'{str(uid)}_{listAlias}'
        with open(f'./data/{filename}.db', encoding='utf8') as f:
            pass
        with open(f'./data/{filename}.db', 'w', encoding='utf8') as f:
            pass
        return 0
    except Exception as e:
        print(f'Error when clearing the database of {str(uid)}: {e}')
        return 1

def deleteAll(uid: any, listAlias: str='') -> int:
    try:
        filename = str(uid) if listAlias == '' else f'{str(uid)}_{listAlias}'
        return os.system(f'rm ./data/{filename}.db')
    except Exception as e:
        print(f'Error when clearing the database of {str(uid)}: {e}')
        return 1

def writeAll(uid: any, toDoList: list[ToDo], listAlias: str='') -> int:
    try:
        db = []
        for toDo in toDoList:
            toDo: ToDo
            stat = 'x' if toDo.isFinished else 'o'
            db.append(f'{stat} {toDo.remark}')
        filename = str(uid) if listAlias == '' else f'{str(uid)}_{listAlias}'
        with open(f'./data/{filename}.db', 'w', encoding='utf8') as f:
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

def getToDo(uid: any, lN: any, listAlias: str='') -> ToDo:
    try:
        toDoList: list = readAll(uid, listAlias)
        assert not -1 in toDoList
        for toDo in toDoList:
            if toDo.lN == int(lN):
                return toDo
        assert False
    except Exception as e:
        print(f'Error when reading a to-do for {str(uid)}: {e}')
        return ToDo('', False, '')

def addToDo(uid: any, remark: str, listAlias: str='') -> int:
    try:
        remark = remark.strip()
        if '&' in remark:
            r1, r2 = remark.split('&', 1)
            return addToDo(uid, r1, listAlias) + addToDo(uid, r2, listAlias)
        else:
            toDoList: list = readAll(uid, listAlias)
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
            status = writeAll(uid, toDoList, listAlias)
            return status
    except Exception as e:
        print(f'Error when adding a to-do for {str(uid)}: {e}')
        return 1

def delToDo(uid: any, lN: str, listAlias: str='') -> int:
    try:
        ls = [int(l.strip()) for l in lN.split('&')]
        toDoList: list = readAll(uid, listAlias)
        newList = []
        assert not -1 in toDoList
        for toDo in toDoList:
            if not toDo.lN in ls:
                newList.append(toDo)
        writeAll(uid, newList, listAlias)
        return 0
    except Exception as e:
        print(f'Error when deleting a to-do for {str(uid)}: {e}')
        return 1

def markToDo(uid: any, lN: any, listAlias: str='') -> int:
    try:
        if isinstance(lN, str) and '&' in lN:
            ls = lN.split('&')
            result = 0
            for each in ls:
                result += markToDo(uid, each, listAlias)
            return result
        else:
            toDoList: list = readAll(uid, listAlias)
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
            writeAll(uid, toDoList, listAlias)
            return 0
    except Exception as e:
        print(f'Error when marking a to-do for {str(uid)}: {e}')
        return 1

def getTag(uid: any, tagname: any, listAlias: str='') -> list[ToDo]:
    try:
        toDoDict: dict = classify(readAll(uid, listAlias))
        if str(tagname) in toDoDict.keys():
            return toDoDict[str(tagname)]
        else:
            return []
    except Exception as e:
        print(f'Error when reading a tag for {str(uid)}: {e}')
        return []
        

def completeAll(uid: any, listAlias: str='') -> int:
    try:
        toDoList = readAll(uid, listAlias)
        newList = []
        assert not -1 in toDoList
        for toDo in toDoList:
            newList.append(ToDo(toDo.lN, True, toDo.remark))
        writeAll(uid, newList, listAlias)
        return 0
    except Exception as e:
        print(f'Error when completing all to-dos for {str(uid)}: {e}')
        return 1

def stat(uid: any) -> list[int]:
    '''
    Only for "Today" view.
    '''
    try:
        toDoList = readAll(uid)
        if -1 in toDoList:
            return [-1, -1, -1]
        else:
            total, finished, unfinished = 0, 0, 0
            for toDo in toDoList:
                if toDo.isFinished == True:
                    finished += 1
                else:
                    unfinished += 1
                total += 1
            return [total, finished, unfinished]
    except Exception as e:
        print(f'Error when doing statistics for {str(uid)}: {e}')
        return [-1, -1, -1]