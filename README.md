## 增加了基本类型直接调用方法的能力

 下面增加了4种常见数据类型的常见方法，包括 \
	 1，列表 \
	 2，字符串 \
	 3，object({}) 类型 \
	 4, set类型  \
  	 5, 同时增加了常见的do{}while(cond)循环
 <hr> 
 
### 列表
1. append
   - 参数：要添加的元素
   - 特点：可以同时添加多个
   - 例子：`append(1, 2)`

2. insert
   - 参数：要插入的位置，要插入的元素
   - 用法：`insert(index, element)`

3. remove
   - 参数：要删除的元素
   - 特点：可以同时删除多个
   - 例子：`remove(1, 2)`

1. removeAt
   - 参数：要删除的索引
   - 功能：删除索引对应的元素 

5. indexOf
   - 参数：要查找的元素
   - 返回值：返回元素的索引，如果没有找到，返回-1

6. count
   - 参数：要查找的元素
   - 返回值：返回元素的个数

7. reverse
   - 无参数
   - 功能：反转列表

8. clear
   - 无参数
   - 功能：清空列表

9. has
   - 参数：要查找的元素
   - 返回值：如果有，返回True，否则返回False

10. setAt
    - 参数：索引，新值
    - 功能：设置指定索引的元素值

11. isEmpty
    - 返回值：布尔值
    - 功能：检查列表是否为空

12. length
    - 返回值：整数
    - 功能：返回列表的长度

13. combine
    - 参数：分隔符
    - 返回值：字符串
    - 功能：将列表元素连接成一个字符串
    - 要求：元素必须是字符串

14. filter
    - 参数：回调函数
    - 返回值：新的列表
    - 例子：
      ```python
			let xlist = [1, 2, 3, 100, 101];  
			let result = xlist->filter(def(x){  
					return x > 10;
			});  
			@println("result:", result);
      ```

15. map
    - 参数：回调函数
    - 返回值：新的列表
    - 例子：
      ```python
			let xlist = [1, 2, 3, 4, 5]
			let result = xlist->map(def(x){ 
				  return x * 2;
			})
			@println("result:", result)
      ```

### 字符串

1. upper()
   - 参数：无
   - 功能：将字符串转换为大写

2. lower()
   - 参数：无
   - 功能：将字符串转换为小写

3. startsWith(prefix)
   - 参数：prefix - 要检查的前缀
   - 功能：检查字符串是否以指定前缀开始

4. endsWith(suffix)
   - 参数：suffix - 要检查的后缀
   - 功能：检查字符串是否以指定后缀结束

5. capitalize()
   - 参数：无
   - 功能：将字符串的第一个字符转换为大写，其余为小写

6. swapcase()
   - 参数：无
   - 功能：将字符串中的大写转换为小写，小写转换为大写

7. split(separator)
   - 参数：separator - 用于分割的分隔符
   - 功能：将字符串按指定分隔符分割成列表

8. strip()
   - 参数：无
   - 功能：去除字符串两端的空白字符

9. isAlpha()
   - 参数：无
   - 功能：检查字符串是否只包含字母

10. isDigit()
    - 参数：无
    - 功能：检查字符串是否只包含数字

11. isAlphaNum()
    - 参数：无
    - 功能：检查字符串是否只包含字母和数字

12. isSpace()
    - 参数：无
    - 功能：检查字符串是否只包含空白字符

13. isLower()
    - 参数：无
    - 功能：检查字符串是否全为小写

14. isUpper()
    - 参数：无
    - 功能：检查字符串是否全为大写

15. concat(str)
    - 参数：str - 要连接的字符串
    - 功能：将给定字符串连接到原字符串末尾

16. charAt(index)
    - 参数：index - 字符的索引位置
    - 功能：返回指定索引位置的字符

17. indexOf(substring)
    - 参数：substring - 要查找的子字符串
    - 功能：返回子字符串在原字符串中首次出现的索引，如果不存在则返回-1

18. contains(substring)
    - 参数：substring - 要检查的子字符串
    - 功能：检查原字符串是否包含指定的子字符串

#### 数据类型转换：

19. ToNumber(str)
    - 功能：将字符串转换为数字

20. ToInteger(str)
    - 功能：将字符串转换为整数

21. ToFloat(str)
    - 功能：将字符串转换为浮点数

22. ToString(obj)
    - 功能：基本类型转换为字符串
    - 注意：number和boolean类型直接转换为字符串

1. ToBoolean(str)
    - 功能：将字符串转换为布尔值


### object{} 类型
 

1. getKeys()
   - 功能：返回字典所有键的列表
   - 返回值：列表

2. getValues()
   - 功能：返回字典所有值的列表
   - 返回值：列表

3. getValue(key)
   - 参数：key - 要查找的键
   - 功能：根据给定的键返回对应的值
   - 返回值：对应的值，如果键不存在则返回 None

4. deleteItem(key)
   - 参数：key - 要删除的键
   - 功能：删除并返回给定键对应的值
   - 返回值：被删除的值
   - 注意：如果键不存在会引发 KeyError

5. update(newDict)
   - 参数：newDict - 包含要更新的键值对的字典
   - 功能：更新字典，将给定的键值对添加到字典中

6. clear()
   - 功能：清空字典中的所有项

7. getItems()
   - 功能：返回字典的键值对列表
   - 返回值：格式为 [[key1, value1], [key2, value2], ...]

8. hasKey(key)
   - 参数：key - 要检查的键
   - 功能：检查字典是否包含给定的键
   - 返回值：布尔值，True 表示包含，False 表示不包含

这些方法提供了操作和访问字典（对象）数据的基本功能，包括获取键和值、更新、删除和检查等操作。
例子：

```js
let obj = {"name":"张三", age: 123};
obj->keys();  // ["name","age"]

obj->getItems(); // [ ["name","张三"], ["age",123] ]

```
### Set类型

length(): int  
	&nbsp;&nbsp;&nbsp;&nbsp;返回集合的长度  
add(element, element2,...): bool  
	&nbsp;&nbsp;&nbsp;&nbsp;是否添加成功  
	&nbsp;&nbsp;&nbsp;&nbsp;可以 一次性增加多个元素
	
```js
let s  =  set<1,2,3, >;  
s->add(4,6);  
@printlnCyan(s);

```
remove(): bool  <br>
	&nbsp;&nbsp;&nbsp;&nbsp;是否删除成功  <br>

clear() : <br>
	&nbsp;&nbsp;&nbsp;&nbsp;清空元素，成功返回True

contains() : bool <br>
	&nbsp;&nbsp;&nbsp;&nbsp;是否包含某个元素  
 
.isSubset(set2) : bool <br>
	&nbsp;&nbsp;&nbsp;&nbsp;调用者是否是set2的子集  <br>

isSuperset(set2) : bool <br>
	&nbsp;&nbsp;&nbsp;&nbsp;调用者是否是set2的超集  <br>

union(set2): set <br>
	&nbsp;&nbsp;&nbsp;&nbsp;返回调用者和set2合并后的集合

intersection(set2) : set <br>
	&nbsp;&nbsp;&nbsp;&nbsp;返回调用者和set2的交集

difference(set2) : set  <br>
	&nbsp;&nbsp;&nbsp;&nbsp;返回调用者和set2的 "difference"

```js
let s  =  set<1,2,3, >;  
s->add(4,6);  
@printlnCyan(s);  
  
s->remove(2);  
let size = s->size();   // 求size
@printlnCyan("size: ${size}");  
@printlnCyan("s = ${s}");  
  
@printlnCyan(s->union(set<100,1000,>));   // 求union
@printlnCyan(s->intersection(set<1,2,100,1000,>));   // 求intersection
@printlnCyan(s->difference(set<1,2,100,1000,>)); // 求difference

```
