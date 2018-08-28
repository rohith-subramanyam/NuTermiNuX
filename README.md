# NuTermiNuX
![NuTermiNuX](../assets/images/NuTermiNuX.png)
## What is it?
**N**u**T**ermni**N**u**X** is terminal and editors configuration for working with Nutanix code base. It helps to eliminate a few inefficiencies that exist today when contributing to or simple browsing through the code base. What are those inefficiencies and how does **N**u**T**ermni**N**u**X** solve them?
### Code browsing
![OpenGrok meme](../assets/images/Code_browsing_OpenGrok_meme.jpg)<br/>
Do you use {OpenGrok to browse Nutanix code base? Do you like it? It is not accurate and does not work all the time as it does not completely understand the semantics of some of the programming languages we use here at Nutanix like Python and Go. Many times, it is simply a git grep over the code base.
![OpenGrok gif](../assets/images/Code_browsing_OpenGrok.gif)

With **N**u**T**ermni**N**u**X**, you can jump into definitions or declarations, including standard library or thirdparty library code wherever the source is available. It setups up paths required for Clang, Go and Python.<br/>
![Code browsing NuTermiNuX gif](../assets/images/Code_browsing_NuTermiNuX.gif)
### Maintaining code quality
![Lint indent meme](../assets/images/Lint_indent_meme.jpg)<br/>
It is a good practice and accepted convention to run linters on our code before submitting them for code review. Except for Clang, in which the upload to gerrit script enforces that no new lint error is added, it is not strictly enforced except during code reviews. Whether they are allowed to commit or not depends on the discretion of the code reviewer and is too late in the workflow and acts as a deterrent for the developer to fix it. It is easier for the reviewer to focus on the business logic when the code submitted for review is free of lint warnings and errors and all the code is vetted by the same set of tools configured the same way.

![Lint precheckin meme](../assets/images/Lint_precheckin_meme.jpg)<br/>
How many times have we seen a silly lint error that could have been caught and avoided creep through causing our pre-commit tests to fail and block check-ins for everyone. Sometimes, it makes it to production causing oncalls.

Every language has its own line continuation rule. Every time I want to continue a long line (> 80 characters) in the next line, I have to lookup the convention. What if you could just hit enter and the editor put the cursor in the right position adhering to the conventions of the language. **N**u**T**ermni**N**u**X** does it for Python and Go.

The common reasons given for not running a linter are:
* I was not aware that there is a convention to run linters
* I do not know which linter to run. There are so many out there.
* There are way too many false positives
* I don't have my linter configured for Nutanix<br/>

**N**u**T**ermni**N**u**X** adds a linter right into your editor. You see lint warning and errors everytime you open a file and updates in real-time as you edit the file. You don't have to leave the editor to fix lint warnings and errors. The linter runs asynchronously and does not block your editing or browsing, so you don't see ghost characters appear seconds after you type. With **N**u**T**ermni**N**u**X**, not only are you more likely to not introduce any new lint warning and errors, you are also more likely to be a good samaritan and fix the existing lint errors if you see them disappear in real-time as you fix them.
For Clang, we use Google's cpplint modified for Nutanix style that is used by the upload review to gerrit script.<br/>
![Lint nolint meme](../assets/images/Lint_NuTermiNuX_nolint.jpg)
### Other inefficiences
When working on a large repository like main, you have to jump into multiple files to use other libraries or dependencies. This is very inefficient as it messes up the context in your head.
**N**u**T**ermni**N**u**X** provides code completion and can complete standard libraries, thirdparty libraries and Nutanix code as well.
![Code completion gif](../assets/images/Completion.gif)
#### Merge conflicts
Do you sweat each time you have to resovle a complex merge conflict? **N**u**T**ermni**N**u**X** provides you a method to perform a 3-way merge showing you the upstream copy on the left, the working copy at the center and the local copy on the right. This makes resolve complex merge conflicts a walk in the park. Sweet!
## Currently Supported:
* VIM
* Languages
  * Clang
  * Go
  * Python
## Prerequisites
\>= CentOS 6.9
```shell
$ cat /etc/centos-release
CentOS release 6.9 (Final)
```
## Install
```shell
$ git clone https://drt-it-github-prod-1.eng.nutanix.com/hackathon-2018/nuterminux.git
$ # or
$ git clone git@drt-it-github-prod-1.eng.nutanix.com:hackathon-2018/nuterminux.git
$ cd nuterminux
$ ./installer/install.py && source "${HOME}/.profile"
$ echo "Do not sweat! All your configurations are backed up and you can rollback"
```
## VIM Cheat sheet
### Code browse
#### Python
```vim
With the cursor on the word, press
,g  " to go to assignment (default goto).
,d  " to go to definition.
Ctrl-o  " to go back.
,n  " show all usages of the name.
K  " to show documentation.
```
#### Golang
With the cursor on the word, press
```vim
gd  " to go to definition.
Ctrl-o  " to go back.
```
#### Clang
With the cursor on the word, press
```vim
"ctags:
Ctrl-]  " to go to definition
Ctrl-t  " to go back.
" For cscope to set the indexes run
:call GenerateTags()  " Key binding <C-/>c
```
### 3-way merge of merge conflicts
```vim
" Open vim and
:Conflicted
" Fix the merge conflicts and
:GitNextConflict  " to cycle through all the conflicted files.
```
### Some other cool things to make you feel like a vim ninja
```vim
,cc  " to comment a VISUAL block or a line.
,c<space>  " to toggle the comment of a VISUAL block or a line.

]c  " to jump to the next change marker.
[c  " to jump to the previous change marker.

" Run git commands right from vim:
:Gdiff
:Gblame
:Gstatus
:Gcommit
" ...
```
## Hey, I want to keep a few of my own custom settings for vim!
Sure, we respect that. Add all your own custom settings to "${HOME}/.vimrc.after" and we will read it.
## Update and Upgrades
If you want to update, it as as easy as
```shell
$ cd nuterminux  # Change to your cloned directory.
$ git fetch origin
$ get rebase origin/master
```
We will let you know how to upgrade as and when we add more and more features mentioned in What next? section.
## Uninstall
We think you will love us and we will stay in your terminal forever, but if for some reason you don't like us?
```shell
$ cd nuterminux
$ echo "Do not run the uninstall as sudo!"
$ ./installer/install.py --uninstall
```
We cleanly rollback all the changes we made to your system and discard ourselves completely. We also restore all your configuration and you are back to where you were before you ran the installer.
## What next?
* If you opt-in, we will add some Nutanix swag to your terminal. How cool will it be if a random ASCII art figure told you a Nutanix principle each time you opened a new session, reminding us what Nutanix stands for.
[!Nutanix ASCII](../assets/images/nutanix_ascii.jpg)
* Setting up PYTHONPATH, GOPATH and any other universal environment setup to work with Nutanix code base
* Support for emacs
* If you opt-in, we will install shell configuration to make your terminal more functional. We will support bash and zsh.
## Questions? Feedback?
Ask on Slack: #nuterminux
## Authors
[Rohith Subramanyam](mailto:rohith.subramanyam@nutanix.com)<br/>
[Anshul Purohit](mailto:anshul.purohit@nutanix.com)<br/>
[Mahesh Venkataramaiah](mailto:mahesh.venkataramaiah@nutanix.com)<br/>
[Vishesh Yadav](mailto:vishesh.yadav@nutanix.com)
