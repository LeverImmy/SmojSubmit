# SmojSubmit
一个可以在[SMOJ](http://smoj.nhedu.net)上提交题目的Sublime Text插件。
  
### 安装
1. 使用`Tools → Command Palette...`打开`Command Palette`；
2. 选择`Package Control: Add Repository`并且按下`Enter`；
3. 输入`https://github.com/YanWQ-monad/SmojSubmit`并且按下`Enter`；
4. 打开`Command Palette`
5. 选择`Package Control: Install Package`并按下`Enter`
6. 找到`SmojSubmit`并按下`Enter`
7. 重启Sublime Text

### 激活
通过修改您的用户配置文件激活SmojSubmit，您可以使用菜单项找到它`Preferences → Package Settings → SMOJ Submit → Setting - User`，
然后你需要在配置文件中输入你的用户名和密码。

### 使用
首先你需要在你的代码中添加如`//1234.cpp`的注释，让它可以检测到需要提交的题号。  
在你的cpp文件中单击右键，
选择 `Submit to SMOJ`, 然后它会提交当前文件到SMOJ。
等几秒钟，它会在新文件中显示你的得分。

### 特性
如果你的代码中出现了像这样的`freopen`：
``` C++
//freopen("Temp.in" , "r", stdin );
//freopen("Temp.out", "w", stdout);
```
或者像这样：
``` C++
/*freopen("1234.in" , "r", stdin );
freopen("1234.out", "w", stdout);*/
```
无需担心，它在提交的时候会把`freopen`的注释去掉，并且改为正确的题号。  
但是如果忘记添加`freopen`，它将不会自动添加。

### Q&A
Q: 为什么我不能单击`Submit to SMOJ`？  
A: 你需要确认你正在编辑cpp文件并且你的用户名和密码是正确的。

Q: 为什么它没有在新文件中显示我的得分？  
A: 因为你正在提交OI模式的题目。

### Bugs
在[这里](https://github.com/YanWQ-monad/SmojSubmit/issues)报告它。
