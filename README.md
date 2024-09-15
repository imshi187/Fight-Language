## 更新 8
1. 增加了完整的类型系统：支持内置数据类型（如int, float）、支持自定义类型（枚举、结构体等）
2. 修改了loop do while for 等语句里return和 break的bug
3. 增加了结构体嵌套和访问能力
4. 完善了函数和方法的默认值
5. 增加了类型判断的内置函数

#### 内置数据类型
数据类型包括： 
	简单数据类型：int float string bool \
	复合数据类型：枚举、结构体、list set object {} \
其他：支持结构体类型、枚举、自定义类作为数据类型

##### 基本数据类型 

```js
$x: int = 1;
let y: string = "abc";
let f: float = 1.1;

let b: bool = True;

let names: list = [];
let set1: set = set<1,2,3, >; // 最后一个需要逗号
let obj: object =  {
	x: 1, 
	name: "fighter!" 
};

```

##### 复合数据类型
结构体和枚举

```js
// 结构体
struct Book{
	Name: string.,
	Price: float 
}
let fight: Book = Book{Name: "fight", Price: 11.1 };

// 枚举 
enum Color{
	RED, GREEN
}

let color: Color = enum::Color::RED; 
printlnCyan(color);

```
类类型

```js
class A {
	fields{}
	methods{
		def PrintInfo(){
				printlnCyan(123);
		}
	}
	init(){}

}
let a: A = new A();
a->PrintInfo();

```
### 默认参数

```js
// 函数默认参数
def add(x: int, y: int = 1) int {
	return x+y;
}
add(1); // y采取默认参数
add(1,y = 100); // 设置默认参数
add(1,2); // y设置为2


// 方法默认参数
class A{
	fields{
		 Id: int = 1;
	}
	methods{
		def Cal(x: float = 2.1, y: float = 1.1) float{
				return x+y;
		}	
	}
	init(){}
}
let a: A = new A();
a->Cal();  // 两个参数都使用默认参数
a->Cal(y = 1.2); // 设置y

```
### 结构体嵌套

```js
struct Info{  
    id: int,    
    age: int
}   
 struct Person{  
    name: string,    
    id: Info   // 嵌套
}  
 let info: Info = Info{     
	    id: 100,        
	    age: 20
};  
  
 let p: Person = Person{    
	 name: "Tom",    
	 id: info 
};  

//或者
 let p: Person = Person{    
	 name: "Tom",   
	 id:  Info{        id: 100,        age: 20    }
 };

// 访问第一层
let v: any = p::id; 
printlnCyan(v);

// 访问第二层
let v2: any = p::id::id; 
printlnCyan(v2);
```
### 类型判断的内置函数

- IsNumber: 判断是否为数组，返回bool
- IsString: 判断是否为string类型，返回bool
- IsBool(val): bool 
- IsInt(val): bool 
- IsFloat(val): bool  
- IsList(val)： bool
- IsObject(val: any ): 判断是否为对象类型，也就是 {} 类型 
- IsSet() bool 
- IsFunction(val: any)： 判断是否是函数; 主要是用于判断匿名函数、箭头函数

```js
let add： function = def(){};
$isfn: bool = IsFunction(add);

```
