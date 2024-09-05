## 模块系统

#### 基本使用方法
可以使用内置模块或者第三方模块

使用内置模块规则：
	将扫描本项目的**builtin** 目录下的文件，模块名称应该和文件名称一直（文件名称多了后缀.fight） \
使用第三方面模块：			
	 使用字符串路径，建议使用**绝对路径**，使用相对路径，解析可能有问题；
```js
// 使用内置模块
use ( foreach ) from ListUtils // 假如再builtin目录下有文件叫做fmt.fight

// 使用第三方模块, 
use ( xx )  from "文件路径"
 
```
#### 模块的声明

模块里面可以声明任何东西，变量、常量、结构体、函数、类、接口、结构体、枚举等，它们之间可以相互引用，比如函数里面使用变量、常量; 

比较好的做法是变量、常量等不要和类、接口放在一起，枚举、结构体等单独放在一起



导出和使用规则：
- 没有被导出的内容（变量，函数等），不能被 use  () from "xx" 使用, 从而也不能使用 
- 被导出的内容在模块内部可以使用未被导出的内容，从而可以访问未被导出的内容，比如
	
```js
// 模块 Test内部
let x = 1;
ley y = x ; // y被导出了，x可以不用导出就能使用

exports = ["y"]


// main 
use ( y ) from Test 
println(y); //  1
```
- 不能导出整个模块，只能按需导出 ，比如下面的做法是错误的：
```js

use Test 
Test.add();  // 错误

```
-  导出的内容和main文件中的内容有重复的地方，会被main文件中的内容覆盖
在ide上应该会有重复声明的提示
```js
// module Test
let y = 1;

exports = ["y"]



// main文件
use (y) from  Test 
let y = 2;
println(y); // 2, 不是1， 会覆盖 

```


#### 典型的模块

1，注意，类建议单独存放，因为类是一个封闭的系统，不能也没必要访问模块内部的内容

例子：
```js


// 模块 Test 
enum Color{  
    Black,White  
}  
  
  
  
let x = 12;  
  
const initCount = x+1;    // 使用模块内部的变量
  
let y = x;  
  
let piAccurate = 3.14159;  
  
const pi = piAccurate;  
  
  
let lst = [1,2,pi];  
  
let set1 = set<1,2,3,False,x,>;  
  
  
def add(item){  
    return 2+item;  
}  
  
  
  
def inc(){  
     printlnCyan("pi = ",pi);  
     return 1+add(10);    // 使用模块内部的函数
}  
  
let keys = {a:1,c:pi};  
  
let set2 = set<1,2,3,False,2,>;  
  
// 访问模块内部的其他常见的内容
let printEnumColor = def(){  
  
    printlnRed("x = ",x);  
    printlnRed("add() = ",add(1));  
    printlnRed("list keys = ",keys);  
    printlnRed("set  set2 = ",set2);  
    printlnRed("const  initCount = ",initCount);  
    printlnRed(enum::Color::White);  
  
    let b = Book{price:100,title:"Java"};  
    printlnRed(b::price,b::title);  
  
}  

// 声明结构体
struct Book{  
    price,  
    title,  
}  
  
interface IFly{  
    Fly();  
}  

// 类
class Person{  
    fields{  
        Gender = "Female";  
  
    }  
    methods{  
        def GetGender(arg){  
            printlnYellow("传进来的参数 = ",arg);  
            return Gender;  
        }  
  
    }  
    init(){}  
  
}  
  
  
exports = [  
    "y",  
    "IFly",  
    "Person",  
    "Book",  
    "Color",  
    "initCount",  
    "add",  
    "printEnumColor",  
    "keys",  
    "lst",  
    "set1",  
    "pi",  
    "inc"  
]



// main中使用模块的内容
use ( inc ) from Test  // 如果Test 是内置模块
use (inc ) from "absPath\Test.fight"



```

#### 模块系统的测试
为了全方位检查模块系统的允许情况，我进行了一下几方面的测试：
1. 正常导出并使用 （导出测试）  
2. 未导出就使用  (未导出测试)  
3. 声明和导出的量（函数等），看查找的顺序 (覆盖性测试)    
        采用覆盖的方法！ main env中的覆盖导入的内容  
4. 导出的量（比如函数）能否使用未导出的量的(类、结构体、接口、类不需要) （内部依赖测试） 
5. 函数、方法是否可以接收外界传入的参数    
6. 模块依赖测试 （一个模块使用另一个模块）

#### 涉及的代码
模块系统涉及的代码：  
    1，use_module方法  
    2，create_closure方法  
    3，evaluate_function_call方法（前面增加了几行代码）


#### 展望
目前的模块系统尚且不足，未来可能会得到优化。

1，缺乏版本管理
2，导入管理需要优化
3，其他（unkown）
