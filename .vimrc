set nocompatible              " 去除VI一致性,必须
filetype off                  " 必须

" 设置包括vundle和初始化相关的runtime path
set rtp+=~/.vim/bundle/Vundle.vim
" set rtp+=/usr/lib/python3.7/site-packages/powerline/bindings/vim

""" Plugins block {
call vundle#begin()
" 另一种选择, 指定一个vundle安装插件的路径
"call vundle#begin('~/some/path/here')

" 让vundle管理插件版本,必须
Plugin 'VundleVim/Vundle.vim'

" enhanced status bar -------------------------------------------------------
Plugin 'vim-airline/vim-airline'
Plugin 'vim-airline/vim-airline-themes'

" disable some extentsions
let g:airline#extensions#fugitiveline#enabled = 0
let g:airline#extensions#wordcount#enabled = 0
let g:airline#extensions#whitespace#enabled = 0

" use powerline fonts
let g:airline_powerline_fonts = 1
" use theme 'deus'
let g:airline_theme = 'deus'

if !exists('g:airline_symbols')
	let g:airline_symbols = {}
endif
let g:airline_symbols.linenr = '¶'
" let g:airline_symbols.whitespace = 'Ξ'

let g:airline_symbols_ascii = 1

" tabline settings
let g:airline#extensions#tabline#tabs_label = 'TAB'
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#show_buffers = 0
let g:airline#extensions#tabline#tab_nr_type = 1
let g:airline#extensions#tabline#tab_min_count = 2
"let g:airline#extensions#tabline#left_sep = '|'
"let g:airline#extensions#tabline#right_sep = '|'
let g:airline#extensions#tabline#formatter = 'unique_tail'
let g:airline#extensions#tabline#show_close_button = 1

" statusbar settings
let g:airline#parts#ffenc#skip_expected_string='[unix]'

" 以下范例用来支持不同格式的插件安装.
" 请将安装插件的命令放在vundle#begin和vundle#end之间.
" Github上的插件
" 格式为 Plugin '用户名/插件仓库名'

Plugin 'tpope/vim-fugitive'

" 来自 http://vim-scripts.org/vim/scripts.html 的插件
" Plugin '插件名称' 实际上是 Plugin 'vim-scripts/插件仓库名' 只是此处的用户名可以省略

Plugin 'L9'

" 由Git支持但不再github上的插件仓库 Plugin 'git clone 后面的地址'
" Plugin 'git://git.wincent.com/command-t.git'

" 本地的Git仓库(例如自己的插件) Plugin 'file:///+本地插件仓库绝对路径'
" Plugin 'file:///home/gmarik/path/to/plugin'

" 插件在仓库的子目录中.
" 正确指定路径用以设置runtimepath. 以下范例插件在sparkup/vim目录下
Plugin 'rstacruz/sparkup', {'rtp': 'vim/'}

" 增强状态栏(no longer support)
" Plugin 'Lokaltog/vim-powerline'

""" 自动补全模块 ------------------------------------------
Plugin 'Valloric/YouCompleteMe'

" see for reference:
"   https://github.com/ycm-core/YouCompleteMe#options 
let g:ycm_use_clangd = 1    " disable clangd
let g:ycm_server_python_interpreter = '/usr/bin/python3'
let g:ycm_global_ycm_extra_conf = '/home/yychi/.vim/bundle/YouCompleteMe/third_party/ycmd/.ycm_extra_conf.py'
let g:ycm_error_symbol = 'E>'
let g:ycm_warning_symbol = 'W>'
noremap <leader>c :YcmCompleter GoToDeclaration<CR>
nnoremap <leader>gf :YcmCompleter GoToDefinition<CR>
nnoremap <C-]> :YcmCompleter GoToDefinitionElseDeclaration<CR>
nmap <F4> :YcmDiags<CR>


""" color scheme ------------------------------------------
Plugin 'liuchengxu/space-vim-dark'

""" 括号匹配 ----------------------------------------------
Plugin 'Raimondi/delimitMate'

""" 对齐增强 ----------------------------------------------
Plugin 'nathanaelkane/vim-indent-guides'
let g:indent_guides_start_level = 2
"let g:indent_guides_enable_on_vim_startup = 1
let g:indent_guides_guide_size = 1
let g:indent_guides_auto_colors = 1

"Plugin 'Yggdroot/indentLine'
"let g:indentLine_char = '|'
"let g:indentLine_color_term = 250
"let g:indentLine_showFirstIndentLevel = 0
"let g:indentLine_enabled = 1
"let g:indentLine_fileType = []
"let g:indentLine_fileTypeExclude = ['text']
"let g:indentLine_bufTypeExclude = ['help', 'terminal']
"let g:indentLine_faster = 1
"let g:indentLine_leadingSpaceChar = '-'
"let g:indentLine_leadingSpaceEnabled = 1


""" 文件树 ------------------------------------------------
Plugin 'scrooloose/nerdtree'

" OPEN A NERDTREE AUTOMATICALLY WHEN VIM STARTS UP IF NO FILES WERE SPECIFIED
autocmd StdinReadPre * let s:std_in=1
autocmd VimEnter * if argc() == 0 && !exists("s:std_in") | NERDTree | endif
autocmd bufenter * if (winnr("$") == 1 && exists("b:NERDTree") && b:NERDTree.isTabTree()) | q | endif
let g:NERDTreeDirArrowExpandable = '▸'
let g:NERDTreeDirArrowCollapsible = '▾'

" shortcut to open fileTree
map <C-n> :NERDTreeToggle<CR>

""" LaTeX 支持 --------------------------------------------
Plugin 'vim-latex/vim-latex'
" REQUIRED. This makes vim invoke Latex-Suite when you open a tex file.
filetype plugin on

" OPTIONAL: This enables automatic indentation as you type.
" filetype indent on

" OPTIONAL: Starting with Vim 7, the filetype of empty .tex files defaults to
" 'plaintex' instead of 'tex', which results in vim-latex not being loaded.
" The following changes the default filetype back to 'tex':
let g:tex_flavor='latex'
" for more settings, pls go to:
" ~/.vim/bundle/vim-latex/ftplugin/tex.vim

""" markdown 支持 ----------------------------------------
Plugin 'godlygeek/tabular'
Plugin 'plasticboy/vim-markdown'
let g:vim_markdown_folding_disabled = 1

""" note taking ------------------------------------------
" Plugin 'vimwiki/vimwiki'

""" snippets support -------------------------------------
Plugin 'SirVer/ultisnips'

" Snippets are separated from the engine. Add this if you want them:
Plugin 'honza/vim-snippets'

" Trigger configuration. Do not use <tab> if you use https://github.com/Valloric/YouCompleteMe.
let g:UltiSnipsExpandTrigger="<leader>e"
let g:UltiSnipsJumpForwardTrigger="<leader>n"
let g:UltiSnipsJumpBackwardTrigger="<leader>p"

" If you want :UltiSnipsEdit to split your window.
let g:UltiSnipsEditSplit="vertical"

""" takswarrior ------------------------------------------
" Plugin 'blindFS/vim-taskwarrior'


" 你的所有插件需要在下面这行之前
call vundle#end()            " 必须
""" }

filetype plugin indent on    " 必须 加载vim自带和插件相应的语法和文件类型相关脚本
" 忽视插件改变缩进,可以使用以下替代:
"filetype plugin on
"
" 简要帮助文档
" :PluginList       - 列出所有已配置的插件
" :PluginInstall    - 安装插件,追加 `!` 用以更新或使用 :PluginUpdate
" :PluginSearch foo - 搜索 foo ; 追加 `!` 清除本地缓存
" :PluginClean      - 清除未使用插件,需要确认; 追加 `!` 自动批准移除未使用插件
"
" 查阅 :h vundle 获取更多细节和wiki以及FAQ
" 将你自己对非插件片段放在这行之后

" ============ user specific ==================="

set laststatus=2
set t_Co=256
set number			" display the number of lines
syntax enable		" auto syntax highlight
"set cursorline		" highlight the cursorline
"set ruler			" display a ruler in statusbar
set tabstop=4		" set the tab length
set shiftwidth=4	" indent length
set softtabstop=4	" >0 other wise tab will insert combination of spaces
set expandtab 		" expand tab to spaces
set noerrorbells	" turn off the error bell
set scrolloff=3	    " 3 lines to top/bottom
"set hlsearch        " highlight matched searching
"set t_vb=			" 置空错误铃声的终端代码	
"set smartindent	" 自动缩进
set showcmd         " show commands
" file encoding families, see: https://www.zhihu.com/question/22363620
set fileencodings=ucs-bom,utf-8,gbk,big5,gb18030,latin1,utf-16
set colorcolumn=80  " draw a vertical line at column 80
""" filetype specification, see: https://segmentfault.com/q/1010000000453410/
autocmd FileType php,python,c,java,perl,shell,bash,vim,ruby,cpp set ai
autocmd FileType php,python,c,java,perl,shell,bash,vim,ruby,cpp set sw=4
autocmd FileType php,python,c,java,perl,shell,bash,vim,ruby,cpp set ts=4
autocmd FileType php,python,c,java,perl,shell,bash,vim,ruby,cpp set sts=4
autocmd FileType tex,javascript,html,css,xml set ai
autocmd FileType tex,javascript,html,css,xml set sw=2
autocmd FileType tex,javascript,html,css,xml set ts=2
autocmd FileType tex,javascript,html,css,xml set sts=2


""" keybindings {
let mapleader=";"
"nnoremap gu gU
"nnoremap gl gu
" space to activate vim cmd
nnoremap <space> :
" jk to escape
inoremap jk <Esc>
" change window-focus keys
nnoremap <leader>j <C-w>j
nnoremap <leader>k <C-w>k
nnoremap <leader>h <C-w>h
nnoremap <leader>l <C-w>l

" For vimdiff.
" see https://stackoverflow.com/questions/161813/how-to-resolve-merge-conflicts-in-git
map <leader>2 :diffget LO<CR> " get from local
map <leader>3 :diffget BA<CR> " get from base
map <leader>4 :diffget RE<CR> " get from remote
""" }


"colorscheme  "solarized gruvbox, molokai, solarized, darkblue, colorsbox, desert, torte, neon

colorscheme space-vim-dark
"set termguicolors
hi Comment cterm=italic
if $TERM ==# "xterm-kitty"
    hi Normal     ctermbg=NONE
    hi LineNr     ctermbg=NONE
    hi SignColumn ctermbg=NONE
endif


""" Gui Settings ============================================================
if has("gui_running")
	" remove sapce at window bottom
	set guiheadroom=0
 	" set guifont=Source\ Code\ Pro\ for\ Powerline\ 16
  set guifont=Consolas\ 14.1
endif

" test git client
