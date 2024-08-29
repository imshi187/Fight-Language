## 增加字面量方法调用、连续调用等
本次更新做了以下改进：
1. 常见类型的字面量调用方法的能力
2. 增强了match表达式
3. 简化了变量声明
4. 增加了绝对值表达式
5. 增加了连续调用（当作纯函数）
6. 增加了列表生成器
7. 简化了方法调用，去掉了@符号

#### 常见字面量调用方法的能力
增加了列表、对象、字符串进行方法调用的能力
比如：

1，字符串字面量调用方法
```js
// 原来的做法
let x = "abc/abc";
let result = x->upper();

//现在
let result = "abc/abc"->upper();

```
2, 列表进行字面量调用的能力

```js
let result = [1,2,3]->combine(",") ;//  字符串"1,2,3"
```
3, 对象进行字面量进行方法调用

```js
let keys = {a:1,b：2}->getKeys(); // ["a","b"]
```

#### 增强了match表达式
主要是增加的else分支

之前必须要列举出所有可能的情况，没法处理缺少的值，现在增加了else分支
```js
$x = 1;
let result = match(x){
	1 => "one",
	2 =>"two",
	else => "other" // else分支	
};

```
#### 简化了变量声明

之前必须使用let进行声明，但是在code过程中发现很繁琐，没有必要，参考php, 使用$作为变量声明的约定


```js
$x = 123; //声明一个x变量
println(x); // 不需要使用$符号
```
#### 增加了绝对值表达式

使用|| 作为绝对值符号，和数学上统一起来
例如：

```js
$x = | 1+2-10 + add(a,b) |;

```

#### 增加了连续调用的能力
这一块终于得到了解决！ fight中，有一个理念，
1，连续调用的时候不改变调用者caller, 也就是当作纯函数看待
2，单独调用某个方法，可能会改变调用者

例子：

```js

// 纯函数
$x = [1,2,3];  // 经过下列两个方法后,x没有改变
x->append(4) // [1,2,3,4]
  ->map(def(item){  //  [2,3,4,5]
		return item+1；
  })->combine(","); // 字符串"2,3,4,5"

// 单独调用某个方法，可能会更改调用者
$x = [1,2,3];
x->append(4); // x变成 [1,2,3,4]


```

#### 增加了列表生成器
基本语法
	generator[element_expr ; var_name = start to end step step_val] \
注意: \
	和 for (idx: 1 to 10)类似，可以是倒序的，也就是从大到小 \ 

例子： 
```js
let x = generator[ idx+1 ; idx = 1 to 3 ];
// x =  [2,3,4] 
```


#### 简化了方法调用，去掉了@符号

之前调用方法必须使用@符号，现在可以去掉

```js
$x = 123;
println(x); // 之前： @println(x);

```
