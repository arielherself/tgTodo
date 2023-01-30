import dbio

ENDL = '\n'
TODO_LIMIT = 20
ERROR_PROMPT = 'We encountered an error when processing your request. Please try again.'

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

def get(uid: any) -> str:
    try:
        result = []
        db = dbio.readAll(uid)
        if len(db) == 0:
            result = ['User does not exist, or your list is empty. Please /register first.']
        else:
            formattedDict: dict = dbio.classify(db)
            for tag in formattedDict.keys():
                result.append(f'#{tag}')
                for toDo in formattedDict[tag]:
                    toDo: dbio.ToDo
                    result.append(format(toDo))
        return '\n'.join(result)
    except Exception as e:
        print(f'Error when formatting the list of {str(uid)}: {e}')
        return ERROR_PROMPT

def add(uid: any, remark: str) -> str:
    remark = remark.strip()
    try:
        if remark == '':
            result = 'Well, please set a to-do like this:\n  <code>/add Have dinner with Ariel</code>\n  <code>/add study #maths</code>'
        else:
            if len(dbio.readAll(uid)) >= TODO_LIMIT:
                result = 'Oops. There are too many to-dos on the list. Please remove some before adding a new one.'
            else:
                ec = dbio.addToDo(uid, remark)
                if ec == 0:
                    result = f'Your to-do is created:\n  <code>{(ENDL+"  ").join([each.strip() for each in remark.split("&")])}</code>'
                else:
                    result = f'We cannot create your to-do at this time. Please try again later.'
        return result
    except Exception as e:
        print(f'Error when handling a "/add" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def mark(uid: any, lN: any) -> str:
    lN = str(lN).strip()
    try:
        if lN == '':
            return 'Please specify a to-do like this:\n  <code>/mark 9</code>\n\nYou can use /get to find the numbering of your to-dos.'
        stat = dbio.markToDo(uid, lN)
        if stat != 1:
            return f'Status of the following to-do is updated:\n<code>{format(dbio.getToDo(uid, lN))}</code>'
        else:
            return f'Cannot make changes to this to-do. Please check if you entered the correct item number.'
    except Exception as e:
        print(f'Error when handling a "/mark" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def delete(uid: any, lN: any) -> str:
    lN = str(lN).strip()
    try:
        if lN == '':
            return 'Please specify a to-do like this:\n  <code>/mark 9</code>\n\nYou can use /get to find the numbering of your to-dos.'
        stat = dbio.delToDo(uid, lN)
        if stat == 0:
            return 'The to-do is deleted.'
        else:
            return f'Cannot delete this to-do. Please check if you entered the correct item number.'
    except Exception as e:
        print(f'Error when handling a "/del" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def tag(uid: any, tagname: str) -> str:
    tagname = tagname.strip()
    try:
        if tagname == '':
            return 'Please specify a tag like this:\n <code>/tag homework</code>'
        else:
            toDos: list[dbio.ToDo] = dbio.getTag(uid, tagname)
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
        if prompt.strip() == 'yes':
            stat = dbio.clearAll(uid)
            if stat == 0:
                return 'Your to-do list is empty!'
            else:
                return 'Cannot clear your list. Please try again later.'
        else:
            return 'Are you sure you want to clear your to-do list? If so, please type\n  <code>/clear yes</code>'
    except Exception as e:
        print(f'Error when handling a "/clear" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def complete(uid: any, prompt: str) -> str:
    try:
        if prompt.strip() == 'yes':
            stat = dbio.completeAll(uid)
            if stat == 0:
                return 'Well done! All your to-dos are completed.'
            else:
                return 'Cannot complete your to-dos. Please try again later.'
        else:
            return 'Are you sure you want to complete all your to-dos? If so, please type\n  <code>/complete yes</code>'
    except Exception as e:
        print(f'Error when handling a "/complete" request from {str(uid)}: {e}')
        return ERROR_PROMPT

def help() -> str:
    return "<b>Welcome to Ariel's To-do Lists!</b>\nTo get started, type /register and then use /add to add a to-do."