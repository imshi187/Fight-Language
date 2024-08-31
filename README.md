## 更新
1，增加了全套的面向对象机制 \
2，全面取消了分号


##### 访问属性  
 - 实例对象访问  
	instance_name->属性名  
- 类访问  
	   类名->属性名   ，其中属性必须是static修饰的  
- init里面访问
	 直接使用字段名称，比如: println("Name = ",Name) 
```js
class Person{
	fields{
		Name = "张三"
		static Height = 1.7 
	}
	 methods{
		 def GetName(){
			 // 方法内部直接使用名称访问
			 println(Name);
		 }
	 }
	 init(){
		 printlnCyan("Name  = ",Name); // 直接使用字段名称进行访问
	 }
}
$p = new Person();
p->Name; // 使用实例对象进行访问
// 访问属性
$height = Person->Height;

```

  
##### 调用方法  

- 实例对象调用  
        instance->方法名()  
- 类调用  
        注意：使用类名只能调用static修饰的方法  
        类名->方法名()  
 
```js
$x =  new Student("102")  
x->PrintInfo();

// 使用类名进行调用静态方法
Student->PrintInfo2()

```
       
##### 初始化  
Init函数是必须的，否则报错  
  
对象初始化          
```js
	let p = new 类名(参数1, 参数2, 参数3...);  
```
或者      
```js
$p = new 类名(参数1, 参数2, 参数3...);  
```

  
init内部对属性的赋值  
``` js
init(name, age){  
        #  字段名称 = 属性名称;  #  
        Name = name;  
        Age = age;  
}  
```
##### init的重载  
fight语言允许多个init函数，会根据传入的参数的个数进行匹配，匹配成功的init函数会被调用  
例如：          
``` js

class Test{
	init(name){  
		  Name = name;  
	}  
	
	init(name,age){  
		Name = name;  
		Age = age;  
	}  
}
$x = new Person("tom");    // 匹配到第一个构造函数  
$x = new Person("tom",99); // 匹配到第二个构造函数  
```

  
##### super关键字   
在init内部可以使用super关键字对从父类继承的属性进行赋值  
    
``` js
init(){  
	  super{  
		父类属性名称: val,  
		父类属性名称1: val2,  
	  }  
}  
```
例子：

```js
interface Walkable{  
	  Walk();  
  }  
  class Person{  
	  fields{  
		  Personality = "empty";  
	  }  
	  methods{  
		  def GetPersonality(){  
			  printlnCyan("Personality = ",Personality);  
		  }  
	  }  
	  init(){}  
  }  

  class Student extends Person implements Walkable{  
	  fields{  
		  Id = 101 ;
		  Name = "Tom";  
		  Age = 18;  
	  }  
	  methods{  
			  def SayId(){  
				  printlnCyan("class_id = ",Id);  
			  }  
			  def SayName(){  
				  printlnCyan("name = ",Name);  
			  }  
			  def GetName(){  
				  return Name;  
			  }  
			  def Walk(){  
				  printlnCyan("I am walking");  
			  }  
	  }  
	  init(id){  
		  Id = id;  
		  super{  
			  Personality:"good",  
		  }  
	  }  
  }  

  $x =  new Student("102");  
  x->GetPersonality();  
  x->Walk();
```
##### 方法内部 
如何调用另一个方法? \
	<span>&emsp;&emsp;</span>this->方法名() <br>
 
访问属性  
	<span>&emsp;&emsp;</span>不需要this  
  
##### 访问权限  
1，大写字母开通的属性、方法为public，小写字母开头的变量、方法为private  
2, 可以使用static解析修饰属性和方法，被修饰的方法直接保存到environment中，可以直接调用  
        形式是: \
		<span>&emsp;&emsp;</span>类名->xxx()  

##### 关于this 
 1. 可以在init内部调用方法:   this->XXX();  
 2. 可以在methods下的方法里进行方法调用： this->XXX();  
 3. 除了以上两个作用，没有其他作用，不可以输出this、return this等。 
  
##### 连续调用  
不需要方法内部返回this来进行链式调用，直接进行链式调用  
例如：  
        
```js
$x = new Person("tom");  
$x->setAge(18)->setName("jerry")->sayHello();  
```
##### 接口 
   
   接口里只能定义方法，建议方法名称大写，因为在实现类里面实现的时候，如果名称为小写，则说明是private方法，无法被外界调用
```js
    interface 接口名{  
         方法名1();   // ; 可以省略
         方法名2();  
    }  
```

实现接口：  
```js
class 类名 implements 接口名{  
        methods{  
            方法名1(){  
                // 实现接口方法1  
            }  
            方法名2(){  
                // 实现接口方法2  
            }  
  
        }  
  
}  
```

##### 继承   
语法：  
        class 子类 extends 父类{}  
	
规则：  
        1，继承父类的public类型的属性和方法  
        2，如果属性或者方法和子类的冲突，则子类会覆盖父类的属性或者方法  
        3，子类可以新增属性和方法，不会影响父类  
  
##### 几个相关方法
   1,IsInstance(对象, 类名: 字符串)：判断对象是否是某个类的实例。  
   例如：  	
``` js
	IsInstance(obj, "Person")：判断obj是否是Person类的实例。  
```

   2,HasImplInterface(类名, 接口名)：判断类是否实现了某个接口。  
   思路：  
	<span>&emsp;&emsp;</span>	判断类里面： 是否包含接口里面定义的全部方法  
   注意：  
	<span>&emsp;&emsp;</span>	仅仅根据是否有接口中定义的方法来判断是否实现了某个接口，而不管使用使用implements关键字  
   例如：  
``` js
HasImplInterface("Person", "Walkable")：判断Person类是否实现了Walkable接口。  
```

##### 多态  
常见场景：
	使用父类接口作为参数，可以接收子类的对象，然后调用方法。  
注意：在fight中，这是天然实现的，因为是动态类型，没有类型限定

 
