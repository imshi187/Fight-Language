### 注意添加的功能
1. 增加了几个内置函数
2. 增加了直接将函数作为参数进行传递的功能（之前是作为变量进行传递）
3. 增加了对列表索引访问和对象访问的嵌套的解析
4. 增加了对返回的函数进行调用的解析
5. 直接了直接返回函数的特性

1，增加的内置函数
增加了输出十六进制、八进制以及二进制的三个函数 ： printlnBin  、printlnHex   、printlnOct
```js
	@printlnBin(3);  // 0b11
	@printlnHex(10); // 0xa
	@printlnOct(9); //  0o11
```
2, 增加了直接将函数作为参数解析传递的特性

```js
	  let z= def(callback,val1,val2){     
		 @callback(val1,val2); 
	 }; 
    	  # 1,  传递箭头函数    #
	 @z(<< x,y,>> =>{      
		  @printlnRed(x*y+1); 
	   },1000,2);  
 
	 # 2, 传递lambda函数 #  
	 let z2= def(callback,val1,val2){     
		 return callback(val1,val2); 
	}; 
	# 1002  #
	@printlnRed( z(lambda x,y : x+y,1000,2) );    


	# 3, 传递匿名函数 #  
	let z2= def(callback,val1,val2){     
		return callback(val1,val2); 
	}; 
	@z(def(x,y){     
		   @printlnRed(x*y+1); 
	},1000,3); //  3001

```
3, 增加了对列表索引访问和对象访问的嵌套的解析 
	访问对象和访问列表可以无限嵌套进行
```js
let z = [ 1,2,{ names : ["Abc", "Jack", "张三"]  } ];
 #   "张三"    #
let r = z[2]{"names"}[2]; 

```
4, 增加了对返回的函数进行调用的解析
	也就是说，如果一个函数返回一个函数，可以直接调用返回的函数，而不是像之前那样还需要先使用变量进行接收, 但是现在最多能支持两层，也就是 callback()()() 这样的是不支持的.

```js
let callback = def(){  
        let cb = def(a, b){            
	        return a + b;        
	    };            
        return cb;  
};  
  
let z = callback()(1,2);

```
5， 增加了直接返回函数的功能

```js
# 返回匿名函数#
let callback = def(){  
    return def(a, b){
	@println(a + b);
   };
};  
  
let z  = callback();  
# 输出: 3 #
@z(1, 2);

# 返回箭头函数#
let callback = def(){  
    return << a, b, >> => {
		@println(a + b);
	};
};  
let z  = callback();  
# 输出: 3 #
@z(1, 2);

```
