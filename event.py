import datetime
import dbio

ENDL = '\n'
TODO_LIMIT = 20
ERROR_PROMPT = 'We encountered an error when processing your request. Please check if you have /register -ed and try again.'

def format(toDo: dbio.ToDo) -> str:
    if toDo.isFinished:
        return f'  <code>[√]{toDo.lN}. {toDo.remark}</code>'
    else:
        return f'  <code>[ ]{toDo.lN}. {toDo.remark}</code>'

def register(uid: any) -> str:
    try:
        if dbio.create(uid) == 0:
            return 'Your list is successfully created. Set your first to-do!'
        else:
            return 'We cannot create a to-do list for you. Please try again later.'
    except Exception as e:
        print(f'Error when handling a "/register" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def get(uid: any, listName: str) -> str:
    try:
        listName = listName.strip()
        result = []
        db = dbio.readAll(uid, listName)
        if len(db) == 0 or -1 in db:
            result = ['List is empty or does not exist. Please /register or /new_list first. Examples:\n  <code>/get</code>\n  <code>/get homework</code>']
        else:
            result = [f'<b>{"Today" if listName == "" else listName}</b>\n']
            formattedDict: dict = dbio.classify(db)
            for tag in formattedDict.keys():
                result.append(f'#{tag}')
                for toDo in formattedDict[tag]:
                    toDo: dbio.ToDo
                    result.append(format(toDo))
        allLists = dbio.seekList(uid)
        if len(allLists) > 0 and listName == '':
            result.append('\n<i>You also have other lists. Use the following commands to access them:</i>')
            for l in allLists:
                result.append(f'  <code>/get {l}</code>')
        return '\n'.join(result)
    except Exception as e:
        print(f'Error when formatting the list of {str(uid)}: {e}')
        return ERROR_PROMPT

def add(uid: any, remark: str) -> str:
    remark = remark.strip()
    try:
        if remark == '':
            result = 'Well, please set a to-do like this:\n  <code>/add Have dinner with Ariel</code>\n  <code>/add study #maths @study</code>\n  <code>/add call Moonstones&write the letter@social</code>'
        else:
            if len(dbio.readAll(uid)) >= TODO_LIMIT:
                result = 'Oops. There are too many to-dos on the list. Please remove some before adding a new one.'
            else:
                remark, *listNames = remark.split('@')
                if len(listNames) == 0:
                    listNames = ['']
                ec = 0
                for listName in listNames:
                    ec += dbio.addToDo(uid, remark, listName)
                if ec == 0:
                    result = f'Your to-do(s) is/are created:\n<code>  {(ENDL+"  ").join([each.strip() for each in remark.split("&")])}</code>'
                else:
                    result = f'We cannot create your to-do at this time. This can be caused by:\n  - misspelling of a list name;\n  - unsupported usage;\n  - server-side error.'
        return result
    except Exception as e:
        print(f'Error when handling a "/add" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def mark(uid: any, lN: any) -> str:
    lN = str(lN).strip()
    try:
        if lN == '':
            return 'Please specify a to-do like this:\n  <code>/mark 9</code>\n  <code>/mark 2&3&4</code>\n  <code>/mark 2&3@lifestyle@homework</code>\n  <code> /mark 4@@fee</code>\n\nYou can use /get to find the numbering of your to-dos.'
        lN, *listNames = lN.split('@')
        if len(listNames) == 0:
            listNames = ['']
        stat = 0
        for listName in listNames:
            stat += dbio.markToDo(uid, lN, listName)
        if stat == 0:
            result = f'Status of the following to-do(s) is updated:\n<code>'
            for listName in listNames:
                result += ENDL.join([format(dbio.getToDo(uid, l, listName)) for l in lN.split('&')]) + '\n'
            result += '</code>'
            return result
        else:
            return f'Cannot make changes to this to-do. This can be caused by:\n  - citation of a nonexistent to-do;\n  - misspelling of a list name;\n  - unsupported usage;\n  - server-side error.'
    except Exception as e:
        print(f'Error when handling a "/mark" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def delete(uid: any, lN: any) -> str:
    lN = str(lN).strip()
    try:
        if lN == '':
            return 'Please specify a to-do like this:\n  <code>/del 9</code>\n  <code>/del 2&3&4</code>\n  <code>/del 2&3@lifestyle@homework</code>\n  <code> /del 4@@fee</code>\n\nYou can use /get to find the numbering of your to-dos.'
        lN, *listNames = lN.split('@')
        if len(listNames) == 0:
            listNames = ['']
        stat = 0
        for listName in listNames:
            stat += dbio.delToDo(uid, lN, listName)
        if stat == 0:
            return 'The to-do(s) is deleted.'
        else:
            return f'Cannot delete this to-do. This can be caused by:\n  - citation of a nonexistent to-do;\n  - misspelling of a list name;\n  - unsupported usage;\n  - server-side error.'
    except Exception as e:
        print(f'Error when handling a "/del" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def tag(uid: any, tagname: str) -> str:
    tagname = tagname.strip()
    try:
        if tagname == '':
            return 'Please specify a tag like this:\n  <code>/tag homework</code>\n  <code>/tag shopping@lifestyle@family</code>'
        else:
            tagname, *listNames = tagname.split('@')
            if len(listNames) == 0:
                listNames = ['']
            toDos: list[dbio.ToDo] = []
            for listName in listNames:
                toDos.extend(dbio.getTag(uid, tagname, listName))
            if len(toDos) == 0:
                return "You don't have any to-dos under this tag."
            else:
                result = f'#{tagname}\n'
                for toDo in toDos:
                    result += format(toDo) + '\n'
                return result
    except Exception as e:
        print(f'Error when handling a "/tag" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def clear(uid: any, prompt: str) -> str:
    try:
        prompt, *listNames = prompt.split('@')
        prompt = prompt.strip()
        if len(listNames) == 0:
            listNames = ['']
        if prompt.strip() == 'yes':
            stat = 0
            for listName in listNames:
                stat += dbio.clearAll(uid, listName)
            if stat == 0:
                return 'Your to-do lists are empty!'
            else:
                return 'Cannot clear your list. This can be caused by:\n  - misspelling of a list name;\n  - unsupported usage;\n  - server-side error.'
        else:
            if len(listNames) == 1 and listNames[0] == '':
                if prompt == '':
                    return 'Are you sure you want to clear your to-do list? If so, please type\n  <code>/clear yes</code>'
                else:
                    return f'Are you sure you want to clear your to-do list? If so, please type\n  <code>/clear yes@{prompt}</code>'
            else:                
                return f'Are you sure you want to clear your to-do list? If so, please type\n  <code>/clear yes@{"@".join(listNames)}</code>'
    except Exception as e:
        print(f'Error when handling a "/clear" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def complete(uid: any, prompt: str) -> str:
    try:
        prompt, *listNames = prompt.split('@')
        prompt = prompt.strip()
        if len(listNames) == 0:
            listNames = ['']
        if prompt.strip() == 'yes':
            stat = 0
            for listName in listNames:
                stat += dbio.completeAll(uid, listName)
            if stat == 0:
                return 'Well done! All your to-dos are completed.'
            else:
                return 'Cannot complete your to-dos. This can be caused by:\n  - misspelling of a list name;\n  - unsupported usage;\n  - server-side error.'
        else:
            if len(listNames) == 1 and listNames[0] == '':
                if prompt == '':
                    return 'Are you sure you want to complete all your to-dos? If so, please type\n  <code>/complete yes</code>'
                else:
                    return f'Are you sure you want to complete all your to-dos? If so, please type\n  <code>/complete yes@{prompt}</code>'
            else:
                return f'Are you sure you want to complete all your to-dos? If so, please type\n  <code>/complete yes@{"@".join(listNames)}</code>'
    except Exception as e:
        print(f'Error when handling a "/complete" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def help() -> str:
    return "<b>Welcome to Ariel's To-do Lists!</b>\nTo get started, type /register and then use /add to add a to-do."

def checkin(uid: any, remark: str, lang: str) -> str:
    try:
        total, finished, unfinished = dbio.stat(uid)
        if total == -1:
            if lang == 'en':
                return 'Unable to get stats now. Please try again later.'
            elif lang == 'zh':
                return '现在无法获取统计信息。请稍后再试。'
            else:
                return ''
        elif total == 0:
            if lang == 'en':
                return 'Have nothing to do today.'
            elif lang == 'zh':
                return '今天没有什么要做的事。又是摆烂的一天？'
            else:
                return ''
        elif total == finished:
            if lang == 'en':
                result = f'{str(datetime.date.today())}\nWell done! You have finished all you {total} to-dos.\n\n<i>"{remark.strip()}"</i>\n\nWhat you finished:\n'
            elif lang == 'zh':
                result = f'{str(datetime.date.today())}\n好活! 你已经完成了你所有的 {total} 项待办.\n\n<i>"{remark.strip()}"</i>\n\n已完成的待办:\n'
            else:
                result = ''
            toDoList = dbio.readAll(uid)
            for toDo in toDoList:
                result += format(toDo) + '\n'
            return result
        else:
            if lang == 'en':
                result = f'You still have {unfinished} to-dos to go:\n'
            elif lang == 'zh':
                result = f'你还有 {unfinished} 项待办没有完成:\n'
            else:
                result = ''
            toDoList = dbio.readAll(uid)
            for toDo in toDoList:
                if toDo.isFinished == False:
                    result += format(toDo) + '\n'
            return result
    except Exception as e:
        print(f'Error when handling an inline query from {str(uid)}: {e}')
        return ERROR_PROMPT

def newList(uid: any, remark: str) -> str:
    try:
        remark = remark.strip()
        if (not remark.isalnum()) and remark != 'Today':
            return 'Please use a list name which only consists of alphabetic and numeric characters. If you want to enter multiple words, consider camelCase. Example:\n  <code>/new_list shoppingList</code>'
        else:
            stat = dbio.create(uid, remark)
            if stat == 0:
                return f'To-do list created: {remark}'
            else:
                return 'We cannot create this list now. Please try again later.'
    except Exception as e:
        print(f'Error when handling a "/newList" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def delList(uid: any, prompt: str) -> str:
    try:
        prompt, *listNames = prompt.split('@')
        prompt = prompt.strip()
        if len(listNames) == 0:
            listNames = ['']
        if prompt.strip() == 'yes':
            stat = 0
            for listName in listNames:
                stat += dbio.deleteAll(uid, listName)
            if stat == 0:
                return 'Your lists are deleted!'
            else:
                return 'Cannot delete your lists. This can be caused by:\n  - misspelling of a list name;\n  - unsupported usage;\n  - server-side error.'
        else:
            if len(listNames) == 1 and listNames[0] == '':
                if prompt == '':
                    return 'Your "Today" list will be deleted. After that, you need to /register before using this service again. Are you sure you want to delete your to-do list? If so, please type\n  <code>/del_list yes</code>'
                else:
                    return f'Are you sure you want to delete your to-do list? If so, please type\n  <code>/del_list yes@{prompt}</code>'
            else:                
                return f'Are you sure you want to delete your to-do lists? If so, please type\n  <code>/delete yes@{"@".join(listNames)}</code>'
    except Exception as e:
        print(f'Error when handling a "/delete" request from {str(uid)}: {e}')
        return ERROR_PROMPT