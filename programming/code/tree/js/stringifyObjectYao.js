// Rewrite stringify object to JSON

const solution = (obj, pretty) => {
    // Type your solution here in JavaScript
    // If you'd like to use Python, use the language dropdown in the upper right
    return stringifyObj(obj, pretty, 0)
};


const stringifyObj = (obj, pretty, level) => {
    let stringObj = ""
    let spacing = ""

    if (pretty) {
        spacing = "\n"
        for (i = 0; i < level + 1; i++) {
            spacing = spacing + "  "
        }
    }

    if (obj === null) {
        return 'null'
    } else if (obj.constructor === Object) {
        stringObj = Object.keys(obj).reduce((arr, key) => {
            listOfString = [...arr, spacing + '"' + key + '": ' +
                stringifyObj(obj[key], pretty, level + 1)]
            return listOfString
        }, []).join(',')
        
        let bracketSpacing = ''
        if(pretty) {
            bracketSpacing = spacing.slice(0, -2)
        }

        return '{' + stringObj + bracketSpacing + '}'
    } else if (obj.constructor === Array) {
        stringObj = obj.reduce((arr, element) => {
            let innerString = stringifyObj(element, pretty, level + 1)
            if(pretty) {
                innerString = spacing + innerString
            }
            return [...arr, innerString]
        }, []).join(',')

        let bracketSpacing = ''
        if(pretty) {
            bracketSpacing = spacing.slice(0, -2)
        }

        return '[' + stringObj + bracketSpacing + ']'
    } else if (obj.constructor === String) {
        stringObj = '"' + obj + '"'
        return stringObj
    } else if (obj.constructor === Number) {
        stringObj = String(obj)
        return stringObj
    } else if (obj.constructor === Boolean) {
        stringObj = ''

        if (obj) {
            stringObj = 'true'
        } else {
            stringObj = 'false'
        }

        return stringObj
    } else {
        return '{}'
    }
};



testObj = {
    "a":{ 
        "b": [1, 3, 4],
        "c": {
            "x": 'bbb',
            "y": 'vvvv'
        }
    } 
}

testObj1 = {
    "a":{ 
        "b": [
            1, 
            3,
            {
                "j": [10000, 2001, 303]
            }
        ],
        "c": {
            "x": 'bbb',
            "y": [6,7,8]
        }
    } 
}

console.log(solution(testObj1, true))
