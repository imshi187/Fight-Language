## 注解系统 
1，注解的适用范围：  
	def关键字定义的函数  
  
```js
def add(a , b) {
	return a +b;
}
```

2， 装饰器的key-value参数  
    value信息可以是基本数据类型或者复杂数据类型，也可以是回调函数（lambda、箭头函数或者匿名函数）;
    如果传入函数名称（作为字符串，比如 funcName = "add"），可以使用InvokeFunc()函数来调用该函数  
  
3, 如何获取注解信息  
    使用 GetFnAnnotations(function_name):  {}  。 获取得到的信息一般格式如下：  
``` js
	{'returnType': 'int', 'paramsNum': 2, 'before': 'beforeCb'}  
```

例子1:  
	 设置普通注解值
```js
@annotation(returnType = "int", paramsNum = 2)  
def add(a, b=10){  
    return a + b;  
}  
let dc = GetFnAnnotations(add);  
@printlnCyan(dc);  //  {'returnType': 'int', 'paramsNum': 2}
```
例子2：
	
```js
#  定义  #
def beforeCb(){  
    @printlnCyan("do sth before the call");  
}  
# before: 设置为函数名称  # 
@annotation(returnType = "int", paramsNum = 2,before = "beforeCb")  
def add(a, b=10){  
    return a + b;  
}  

#获取函数的注解信息#
let dc = GetFnAnnotations(add);  
  
#   {'returnType': 'int', 'paramsNum': 2, 'before': 'beforeCb'}  #  
@printlnCyan(dc);  
  
  
# 注解: 实现某种程度的装饰器模式#  
if(dc{"before"} != ""){  
    #  调用beforeCb函数  #  
    @InvokeFunc(dc{"before"},{});  
}

```
例子3：
	传入回调函数进行增强
```js
#传入回调函数#
@annotation(before = def(){ @printlnCyan("事前调用"); }, after = << >> =>{ @printlnCyan("事后调用"); } )  
def add(a, b=10){  
    return a + b;  
}  
#获取注解信息#
let dc = GetFnAnnotations(add);  
@printlnCyan("dc: ",dc);  
  
  
if(dc{"before"} != ""){  
    @printlnCyan("before info:  ",dc{"before"});  
     #获取函数并执行#
    let fnBefore = dc{"before"};  
    let fnAfter = dc{"after"};  
    @fnBefore();  
    @fnAfter();  
}

```
