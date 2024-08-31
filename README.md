## Fight Language Tutorial
### 更新
更新1 (2024/8.15) : [增加了可以直接传入函数的特性 & 增加了几个进制方面的输出](https://github.com/imshi187/Fight-Language/tree/%E6%9B%B4%E6%96%B01-%E5%A2%9E%E5%8A%A0%E7%B3%BB%E5%88%97%E5%86%85%E7%BD%AE%E5%87%BD%E6%95%B0%E5%92%8C%E5%87%BD%E6%95%B0%E4%BD%9C%E4%B8%BA%E5%8F%82%E6%95%B0%E4%BC%A0%E5%85%A5%E7%9A%84%E6%94%AF%E6%8C%81) : 已加入到main branch

更新2 (2024/8.17) : [增加了可以枚举enum & 结构体struct & 反射](https://github.com/imshi187/Fight-Language/blob/%E6%9B%B4%E6%96%B02-%E5%A2%9E%E5%8A%A0%E5%8F%8D%E5%B0%84-%26-%E6%9E%9A%E4%B8%BE-%26-%E7%BB%93%E6%9E%84%E4%BD%93%E5%8A%9F%E8%83%BD/README.md) : 已加入到main branch

更新3 (2024/8.18):  [增加了函数注解，极大地加强了函数能力](https://github.com/imshi187/Fight-Language/tree/%E6%9B%B4%E6%96%B03-%E5%87%BD%E6%95%B0%E6%B3%A8%E8%A7%A3): 已添加到main branch 

更新4 (2024/8/19 和 8/22): [增加了基本数据类型进行方法调用的能力 & 类的注解系统 & do_while循环](https://github.com/imshi187/Fight-Language/tree/%E6%9B%B4%E6%96%B04-%E8%AE%A9%E5%9F%BA%E6%9C%AC%E6%95%B0%E6%8D%AE%E7%B1%BB%E5%9E%8B%E5%8F%AF%E4%BB%A5%E5%83%8F%E5%AF%B9%E8%B1%A1%E4%B8%80%E6%A0%B7%E8%B0%83%E7%94%A8%E6%96%B9%E6%B3%95): 已加入到main branch

更新5 (2024/8/29): [增加字面量方法调用、连续调用、列表生成器等重要内容](https://github.com/imshi187/Fight-Language/blob/%E6%9B%B4%E6%96%B05-%E5%A2%9E%E5%8A%A0%E5%AD%97%E9%9D%A2%E9%87%8F%E6%96%B9%E6%B3%95%E8%B0%83%E7%94%A8%E3%80%81%E8%BF%9E%E7%BB%AD%E8%B0%83%E7%94%A8%E7%AD%89/README.md) 

更新6 (2024/8/31): [完善了面向对象机制  & 全面取消了分号](https://github.com/imshi187/Fight-Language/tree/%E6%9B%B4%E6%96%B06-%E5%AE%8C%E5%96%84%E4%BA%86%E9%9D%A2%E5%90%91%E5%AF%B9%E8%B1%A1%E7%89%B9%E6%80%A7-%26-%E5%8F%96%E6%B6%88%E4%BA%86%E5%88%86%E5%8F%B7)


### Requirements (重要) 

1, python 版本为3及其以上 , 涉及第三方库较少，建议使用pycharm 进行自动安装

2，说明：<br> 
<span>&emsp;&emsp;</span> Evaluator.py中的 from interpreter.xxx  import xxxNode， interpreter指的是interpreter目录，也就是本项目在本地运行时需要将本项目的根目录改为 interpreter 。
具体可以看proj_structure.png作为参考


### 简介
   - 语言概述
 
 
特点：
	fight语言写到现在，没有引入很多复杂性，其中大部分特性和python, js接近，比如解构赋值，比如箭头函数，其他的则是和python接近（实际上本语言就是使用python完成的），比如几个数据结构: dict, set,  以及list。 除此之外，我尝试引入更多其他语言的一些特性，比如rust的match(){}匹配， loop结构。待到基本完成之时，发现居然和最近的仓颉语言有很多相似性 。😂

未来：
	 本项目到现在为止，以及完成了绝大部分功能，包括控制结构（for in , for(idx: 1 to 10) ,loop, if elif ,switch等） 、函数（匿名函数、箭头函数、def定义的函数，命名参数，参数默认值，位置参数，高阶函数，闭包等）、类机制、模块机制、异常机制、常见的数结构(dict, list, string, bool, number, set等)，等等，期待引入其他特性， 比如线程、异步、装饰等

### 基础语法
   - 变量声明和赋值 (let, const)
   - 数据类型 (数字、字符串、布尔值，object , set, list)
   - 运算符 (+, -, *, /, ^, %, //, ==, !=, >, <, >=, <=)
   - 注释 (# 注释内容 #)

变量声明和赋值
	使用 let关键字进行声明和赋值，比如:	
```js
let x = 123;
#  使用模板字符串 #
let x = "hi, ${x}";  
```
常量声明
	使用关键字 const进行声明 
```js
const port = 9090;  
port = 100;  // 错误，不可更改
```

运算符
	常见的运算符都支持，特别地，引入几种少见地运算符：
	// ：整除运算
	% : 取余运算

两个特殊的表达式
1，match表达式
	
```js
let returnVal = 2;
let x = match(returnVal) {
	1 => "one",
	 2 => 'tw0",
	 100 => "huandred"
}; 
```

2， if 三目运算符

```js
let x = if( 10 > 1) 10 : 1;   // x=10
```


注释
	在fight语言中，使用##进行注释，支持单行和多行，例如：
	
```python
# 我是单行注释, 下面的结果是: 0  #
let z = 10 // 2; 

#
 1，x是number类型
 2，s是字符串类型
#
let x = 123;
let s = "";
```
1. 控制流
   - if-elif-else 语句
   - for 循环 (包括 for-in 和数字范围循环)
   - break 语句
   - loop循环
   - switch 语句
if-elif-else
	
```js
let x = "B";
if ( x == "A"){
	// code

} elif (x == "A") {

	// code
} else {
	// code

}

```


for循环由两种，
	for in 循环，可以遍历列表、字符串、集合(set)以及对象object，比如  

```js
#  遍历列表  #
for(element in [1,2,3]){
   @printlnRed(element);
}
 # 遍历字符串 @ 
 for(ch in "fight"){
    @printlnCyan(ch);// f i g h t 
}
 
# 遍历对象 # 
let obj = {a:1,b:2};
for(key in obj){ 
    @printlnCyan(obj{key}); # a b
}
  
# 遍历集合set #
let obj = set<1,2,"字符串", >;
for(element in obj){
    @printlnCyan(element);
}


```
2) for 遍历 数字，类似 for range
    
```js
for (idx : 1 to 10){
	  // forward   1 2 3 ...
	@printlnCyan(idx);
}

// backward
for (idx: 10 to 1){ 
	@printlnRed(idx); // 10 9 8 ...
}

```
loop循环
	
```js
let x = 10;
 loop(x>0){
	 @println(x);
	 x--;
 }

```

switch语句

```js
let x = 2;
switch(x){
	case(1){
			// code
	}
	case(2){
			// code
	}
	default{  
		// code
	}

}
```



### 复杂数据类型
   - 列表 (创建、访问、修改)
   - 对象 (创建、属性访问)
   - Set 类型  
	
```js
let x = [1,2,3];
@println(x[1]); // [2]
@println(x[0:1]); // [1,2]
@ListAppend(x,10) // 添加元素

```
关于列表，内置了一些常见的函数，具体可以可以查看utils下的ListUtils,  比如:

```js

ListLength
ListAppend
ListInsert
ListRemove
ListCount
等等


```


对象
	也就是dict类型，别入 let x = {a : "a"}; 和js类似
     关于object类型，在utils / DictUtils 下也写了一些方法

set类型
	
```js
let s = set<1,2,True, > //最后一个需要使用逗号分割

```
关于set类型，也提供了一些方法， 比如SetLength() 等，具体如下, 具体的方法内容在Evaluator.py中有，可以在该文件内进行搜索即可
```js
SetLength
SetAdd
SetRemove
SetContains
SetIsSubset
SetIsSuperset
SetClear
SetUnion
SetIntersection
SetDiff
```



### 函数
   - 函数定义和调用
   - 参数传递 (位置参数、默认参数、命名参数)
   - 返回值
   - 匿名函数 (lambda 表达式)
   - 箭头函数
   - 高阶函数

函数定义
	在fight中提供了4种函数，普通定义的函数、匿名函数、lambda函数以及箭头函数
``` js
// 普通函数
def add(a, b){
	return a+b;
}

// 匿名函数
let  inc = def(x){
	return x+1;
};  // 需要使用逗号


// lambda函数
let lmbd = lambda x,y : x+y;

// 箭头函数
let arrow = << x, y , >> =>{
	 // 可以在内部定义函数
	def inc(x){
			return x + 1;
	}
	 return inc(x+y);
};
```

函数的调用
	1,无论是哪一种函数，如果作为语句进行调用，也就是不获取返回值，那么就需要@ 符号，如果作为表达式（比如let a = add(1,2) ）, 不需要@ 。
	2, 实际上，这种设计一开始来源于对复杂情况考虑不周，现在木已成舟，可能后期再努力努力吧。
	 下面给出几个例子:	

```js
// 1, 单独的调用，不需要@
 @add(1,2);
// 需要返回值，不需要@
let result = add(1,2);

// 作为函数值传递给另一个函数，不需要@
let result = inc( add(1,2) ); 


```

高阶函数
	高阶函数是fight语言一大特色，在fight语言中，支持使用函数作为参数传入，支持返回函数，支持在一个函数内部定义另一个函数等等，具体看如下的演示。

高阶函数：
```js
def foreach(xlist,callback){
   for( ele in xlist)
	   @callback(ele);
}

let myprint=  def(x){
	@printlnRed(x);
};
let list = [1,2,True, "Msg",{a:1}];
@foreach( list,myprint);

```

返回一个函数: 

```js
let z =def(){
	let inc = def(x) {  @printlnRed("ok") };
	 return inc;
};
let cb = z(); 
@cb(); 
```
暂时不支持的函数传入:

```js
let filter = def(xlist,predicate){
	let result = [];
	 for(element in xlist){ 
		 if(predicate(element)){ 
			 ListAppend(result, element);
		 }
	 } 
	 return result; 
};
// 正确的函数传入：先用变量接收再传入
let gt2 = def(x){ 
	if(x>2){ return True; }
	 else{
		 return False;
	 } 
};
let filtered = filter([1,2],gt2);

// 错误的函数传入: 不能直接传入整个函数，需要先使用变量接收
let filtered = filter([1,2],def(x){
	 if(x>2){ return True; }
	 else{
		 return False;
	 }				
});

```





### 字符串处理
   - 字符串方法 (利用在utils/StringUtils里面复用python的字符串方法)
   - 模板字符串

字符串方法，和其他语言，特别是python语言，没有多大差异，不过在fight语言中，对复杂数据类型的操作方法都是函数式方法，比如StrIndex, ListAppend, ObjContains(), SetDiff等，咋不说不支持面向对象那样的调用， 比如下面的代码，更多的方法参考 utils / StringUtils.py 
```js
let s = "abc";
@println( StrLength(s) );
@println ( StrIndex("a") ); 
```


模板字符串
	fight支持模板字符串，比如:
	
```js
let s = "fight";
let p = " hello, ${ s } ";


```

###  面向对象编程
   - 类的定义和实例化
   - 构造函数
   - 方法和属性
   - 继承
   - 静态方法和静态属性
   - 接口和实现

fight语言支持简单的类机制，下面是一个例子:

```js
class Person{  
	     fields{         
		      Name = "abc";          
		      Age = "25";     
		      static Count = 0; 
		}      
		methods{          
			def Hello(){             
				@printlnRed("Hello, my name is " + Name);             
				this->hi();          
			}          
			def hi(){                       
				@printlnCyan("Hi, my name is " + Name);  
	             		@printlnCyan("Hi, age = " , Age);          
	       		 }          
	        	static def PrintMsg(msg){                        
			        @printlnYellow(msg);  
	          	}      
	    	}      
	    init(NameX){          
		    Name = NameX;          
		    Age = 100;  
	        @printlnYellow("Person object is created!");
           }  
 } 
 
 let p = new Person("Abc");  
 p->Hello();  #  Hello, my name is Abc #   
Person->PrintMsg("Hello, world ");  #  Hello, world #
@printlnRed(Person->Count); 

```

几条规则：
1. 方法内部可以使用this互相调用， 属性调用不需要this, 直接写属性名称  
2. 静态属性或者方法直接使用类名进行调用 ，不可以使用实例对象进行访问
3. this除了用来调用方法，再无其他作用，这里显示了fight在类机制上的不足，也就是说，没法返回this来进行链式调用
4. 大写的属性或者方法表示是public的，小写的表示为private的，fight语言不支持使用public或者private进行修饰，但是可以使用static进行修饰

继承
1. 使用extends就行继承，仅仅支持单继承，但是可以使用implement实现多个接口
2. extends的作用：
		- 继承父类public类型的属性和方法，其他一概不管; 
		- 其中static的属性和方法也没有继承过来
	
``` js
class Dog extends Animal{
     fields{}
     methods{}
	init(){}
}
```

接口和实现
	fight中的接口很简单，就是对实现类方法的约束，在接口中声明的方法必须要在类中进行实现
	
```js
interface Flyable{
	Fly();

}
// 实现接口中声明的方法
class Brid implements Flyable{
	methods{
		def Fly(){
				// code
		}
	}

}

```



### 异常处理
   - try-catch-finally 语句
   - 异常类型
异常处理机制实际上就是借用python的异常机制，相对来说没有很完善，用法如下。其中异常的名字和python中异常的名字完全一致，如果要增加新的异常类型，在 Evaluator.py下的evaluate_try_catch_finally()方法中定义的exception_mapping进行增加

```js
try {

	// code
	 let z = 1/0;

}catch(ValueError){


}catch(xxError){



}finally{
	// code
}

```

### 模块系统
   - 模块的导入和使用
模块定义
	使用package关键字进行定义，使用import 关键字进行导入。实际上，导入机制并不完善，因为现在导入的代码都需要在同一个文件内部，没有处理跨文件导入
```js
package Math{
	const pi = 3.1; 
	 let lmd = lambda x : x+1;
	 def inc(x){ 
		 return x + 1;
	 }

}
// 导入模块并使用
import Math  
@println(Math.pi)
@Math.inc(12); 

// 部分导入
import { pi } from Math 
import { inc } from Math 

let z = inc(100); 

```




### 内置函数和库
    - 列表操作 
    - 类型转换函数 (ToNumber, ToString 等)
    - 时间相关函数
    - 数学函数
    - 随机数生成
    - 文件和操作系统操作
 以上各个模块的方法都复用自python的模块，比如list方法，random模块的方法，os模块的方法，以及time的几个方法，具体可以参考utils里面的内容


### 高级特性
两种解构赋值: list解构，object解构

```js

// object解构
let obj = {a: 1, b: 2};
let {a,b} = obj; // a: 1  b: 2 

// list解构
let [x,_,z] = [1,2,3];  
@println(x,z); // x = 1, z = 3


```


### 调试和开发工具
为了更好地支持输出，内置了几个打印函数，可以设置字体的颜色，也可以设置几种背景，具体如下，
 如果需要增加其他的，可以在Evaluator.py的evaluate_function_call方法中查看代码:
 
```js
color_map = {  
    'println': (Fore.RESET, None),  
    'printlnRed': (Fore.RED, None),  
    'printlnYellow': (Fore.YELLOW, None),  
    'printlnBlue': (Fore.BLUE, None),  
    'printlnCyan': (Fore.CYAN, None),  
    'printlnRedBg': (Fore.RESET, Back.RED),  
    'printlnLightGreen': (Fore.LIGHTGREEN_EX, None)  
}

@printlnRed(12); 

```




 ### 展望
 
 fight语言现在面临几个问题：
1. 没有vscode或者idea插件支持，现在只能使用字符串形式或者txt等文件格式进行书写，没有高亮、代码提示，尤其是没有检查 (作者尝试vscode插件编写学习,感觉很受挫)
2. 类的机制不完善，这个可操作空间比较大
3. 没有类似npm这样的模块管理机制
4. 线程：不支持，也没有异步
5. 速度上：现在使用python开发，后期可能会考虑使用其他语言重新开发。比如rust, java 

### 期待
 
如果你对fight语言感兴趣，有什么新奇的想法，想要加入新的特性，或许可以加入到fight语言的建设中来。如果您觉得fight还挺好玩，不妨试试给它写个vscode插件，提个建议。现在就我一个人在维持该项目，经验不足，期待您的加入。😘😂😍
 
 
