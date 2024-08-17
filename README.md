### 反射特性  
1. 关于函数的反射
2. 关于类的反射
  
关于函数的反射

   1, GetParamsByName  
	通过函数名称获取函数的参数           
	例子 ： 
```js

def add(a, b=10){  
	 return a + b;  
}  
let info = GetParamsByName("add"); 
@printlnCyan(info);    #  ['a', 'b']  #  
  
```

2, GetDefaultValues  
	通过函数名称获取函数的默认参数，返回存在默认参数的字典,比如:  {'b': 10} 。可以通过遍历key来判断某个参数是不是存在默认值 。  
例子:  
                 
``` js
def add(a, b=10){  
	 return a + b;  
 }  
 let info = GetDefaultValues("add");  
 @printlnCyan(info);  
```
3, InvokeFunc ("FuncName",{param: value, param2: value2})  
	  通过函数名称和参数列表调用函数，返回函数的返回值 。注意：第一个参数不是类或者实例的方法，而是单纯的函数                                           
``` js
let cb = def(cb,x = 3){  
		@printlnCyan(x);  
		@cb();  
};  
@InvokeFunc("cb",  {  x: 5,  
				cb: def(){  
					@printlnYellow("hello world");  
				}  
			}  
);  
```

**关于类的反射**

1, GetFieldsByClassName  
	通过类名称获取类的字段，返回一个字典，  
	比如:  
	    
``` js
{'Name': 'Fight从入门到精通'}  
```
 
 **关于实例的反射** 

1, GetInstanceFields  
	通过实例对象获取实例的字段，返回一个字典，{x:1}  
	例如：  
                    
``` js
  let  cv = new Book(10000);  
 @printlnCyan("fields: ",GetInstanceFields(cv));
```
  
 **获取实例的方法名称**  
 
1, GetInstanceMethods(instance) 
	通过实例返回实例的方法名称，返回一个列表，每个元素是一个字典，包含方法名，参数列表，默认参数列表  
	比如:         
```js
[  
	{'args': ['x'], 'default_values': {'x': 123}, 'method_name': 'Test'},  
	{'args': [], 'default_values': {}, 'method_name': 'Print'},  
]  
```
例如：                  
``` js
let  cv = new Book(10000);  
@printlnCyan("methods: ",GetInstanceMethods(cv));  
```

 2，InvokeInstanceMethod(instance, method_name, params: {})  
     比如:
		InvokeInstanceMethod(cv, "Test",{x: 5});  
	注意：  
		1，三个参数： 实例，方法名，参数字典  
		2，方法名是字符串类型，参数字典是键值对形式，键是参数名，值是参数值  
		3，方法名和参数名要和定义的一致，否则会报错  
		4，也就是说，该方法只能使用命名参数  
                 
``` js
class Book{  
		fields{  
			Name = "Fight从入门到精通";  
			Price = 99;  
		}  
		methods{  
			def Test(x = 123,z){  
				@printlnCyan("book test...",x,z);  
			}  
			def Print(y = [1,2,3]){  
				@printlnYellow("book name: ",Name);  
				@printlnYellow("book price: ",Price);  
			}  
		}  
		init(price){  
			Price = price  
			@printlnCyan("book init...");  
		}  
   }  
  let  cv = new Book(10000);  
  @InvokeInstanceMethod(cv, "Test",{ x: 5,z: [1,2,3]});  
  
```

3, SetInstanceField
    通过属性名称和值动态设置实例的属性。                
    SetInstanceField(instance, {field_name: value})  
    比如:  
                      
``` js
let  cv = new Book(10000);  
@printlnCyan("Name =  ",cv->Name);  

@SetInstanceField(cv,{Name: "Javascript从入门到精通"});  

@printlnCyan("Name =  ",cv->Name);  
```

### enum类型  
枚举类型定义，比如：           
	
``` js
enum Color {
	Red, Green, Blue
};  
```

赋值  
	
``` js
 let x = enum::Color::Red;;  
```

比较  
``` js
if ("Red" == enum::Color::Red) {  
		// do something  
} 
```
 
实质  
	   &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fight中枚举类型就是字符串类型, 可以拿其值与字符串进行比较。 其他语言如c, 枚举值背后是数字  
 
改进            
	  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;存放数字类型，减小存储空间； 因为每个字符占据一个字节，但是数字一般就一两个字节   但是其实差异不大  
    例子:  
``` js
enum Color {  
		Red, Green, Blue  
  }  
  let x = enum::Color::Red;  
  let y = enum::Color::Green;  

  @printlnCyan(x,y);  

  if(enum::Color::Red == "Red"){  
	  @printlnCyan("Red");  
  }  
```

### struct结构体  

声明
```js
struct Point {  
	x, y    // x, y为属性名称
}  
```

赋值        
	let p1 = Point{x: 10, y: 20};  
访问  
	 let val =  p1::x;  
  
**赋值语句的特性：**  
  
  1，可以覆盖  
		
``` js
let p = Point{x: 10, y: 20};  
p = Point{x: 30, y: 40};    // 必须全部重新赋值，
```
2, 部分更新  
  使用方法进行更新 ，可以考虑再赋值，但是需要每个属性都要重新赋值           
		 &nbsp;&nbsp;&nbsp;&nbsp;partialUpdate(struct_instance,{key:newValue}) : bool  
	 
  返回值  
		 &nbsp;&nbsp;&nbsp;返回 False 或者 True 表示是否成功  
	  例子 ：          
```js
struct Point {  
	x, y  
}  
let p = Point{ x : 1, y: 2};  
 
@printlnCyan(p::y);  
@partialUpdate(p, {x: 4}); // True
```
