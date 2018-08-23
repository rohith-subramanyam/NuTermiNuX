;; Emacs by NuTermiNuX
;;
;;----------------------------------------------------------------------------
;; Initialize Packages
;;-----------------------------------------------------------------------------

(require 'package)

(setq package-archives
  '(("gnu" . "https://elpa.gnu.org/packages/")
    ("marmalade" . "https://marmalade-repo.org/packages/")
    ("melpa" . "https://melpa.org/packages/")
    ("melpa-stable" . "https://stable.melpa.org/packages/")))

(add-to-list 'load-path "~/.emacs.d/lisp/")

(defvar my-packages
  '(;; Basics
    better-defaults
    bind-key

    ;zoom-frm
    ace-window
    switch-window
    smex
    idle-highlight-mode

    ;; Ido
    ido-ubiquitous
    flx-ido
    ido-occur

    ;; Search
    ag

    ;; Project Management & Find files
    fzf
    command-t
    find-file-in-project
    projectile

    ;; git
    magit
    diff-hl

    ;; Helm modes
    helm
    helm-ls-git
    helm-cmd-t
    helm-ack
    helm-ag
    helm-codesearch
    helm-gtags
    helm-fuzzy-find
    helm-flycheck
    helm-google
    helm-swoop

    ;; Flycheck modes
    flycheck

    ;; Go
    go-mode
    go-autocomplete
    go-eldoc

    ;; Markdown
    markdown-mode+
    markdown-preview-mode

    ;; JavaScript
    js2-mode
    json-mode
    web-mode
    exec-path-from-shell

    ;; C/C++
    ggtags
    protobuf-mode

    ;; Python

    ;; Themes
    zenburn-theme
    ))

(package-initialize)

(when (not package-archive-contents)
  (package-refresh-contents))

(dolist (p my-packages)
  (when (not (package-installed-p p))
    (package-install p)))

;; Our elisp library
(load-file "~/.emacs.d/lisp/lib.el")

;;---------------------------------------------------------------------------
;; Misc
;;---------------------------------------------------------------------------

; Disable startup splash
(setq inhibit-splash-screen t)

;; Set PATH environement variable
(setenv "PATH" (concat (getenv "PATH") ":/usr/local/bin:"))
(setq exec-path (append exec-path '("/usr/local/bin")))

;;; For Mac OSX weird redraw bug on bell
(setq ring-bell-function (lambda () (message "*woop*")))

;; https://github.com/purcell/exec-path-from-shell
;; only need exec-path-from-shell on OSX
;; this hopefully sets up path and other vars better
(when (memq window-system '(mac ns))
  (exec-path-from-shell-initialize))

;;---------------------------------------------------------------------------
;; Look and Feel
;;---------------------------------------------------------------------------
(set-default-font "Inconsolata 12")

(menu-bar-mode -1)
(tool-bar-mode -1)
;(scroll-bar-mode -1)

; Line numbers
(setq linum-format "%3d ")
(setq tab-width 4)

;; Show column numbers in mode line.
(setq column-number-mode t)

(when window-system
  (load-theme 'zenburn t)
  ;; change vertical border
  (set-face-background 'vertical-border "lightblue")
  (set-face-foreground 'vertical-border (face-background 'vertical-border)))

(with-eval-after-load "zenburn-theme"
  (zenburn-with-color-variables
    (custom-theme-set-faces
     'zenburn
     ;; original `(default ((t (:foreground ,zenburn-fg :background ,zenburn-bg))))
     `(default ((t (:foreground ,zenburn-fg :background ,zenburn-bg-2)))))))

; default scrolling sucks :/
(setq scroll-step 1)
  (setq scroll-conservatively 10000)
  (setq auto-window-vscroll nil)

(setq scroll-preserve-screen-position 'always)
(global-set-key [next] 'scroll-up-half)
(global-set-key [prior] 'scroll-down-half)

;;----------------------------------------------------------------------------
;; Ido modes
;;-----------------------------------------------------------------------------

(ido-mode 't)

;; --------------------------------------------------------------------------
;; Helm modes
;;-----------------------------------------------------------------------------

(setq helm-swoop-speed-or-color t) ;;; helm-swoop color

;;---------------------------------------------------------------------------
;; Project

(projectile-global-mode)

;;----------------------------------------------------------------------------
;; Flycheck
;;-----------------------------------------------------------------------------

(require 'flycheck)

;; turn on flychecking globally
(add-hook 'after-init-hook #'global-flycheck-mode)

;; disable json-jsonlist checking for json files
(setq-default flycheck-disabled-checkers
  (append flycheck-disabled-checkers
    '(json-jsonlist)))

;; customize flycheck temp file prefix
(setq-default flycheck-temp-prefix ".flycheck")

(setq flycheck-highlighting-mode 'lines)

;;------------------------------------------------------------------------------
;; Go
;;-----------------------------------------------------------------------------

(defun auto-complete-for-go ()
  (auto-complete-mode 1))
(add-hook 'go-mode-hook 'auto-complete-for-go)
(with-eval-after-load 'go-mode
   (require 'go-autocomplete))
(add-hook 'go-mode-hook 'go-eldoc-setup)


(defun my-go-mode-hook ()
  ; Call Gofmt before saving
  (add-hook 'before-save-hook 'gofmt-before-save)
  ; Customize compile command to run go build
  (if (not (string-match "go" compile-command))
      (set (make-local-variable 'compile-command)
           "go build -v && go test -v && go vet"))
  ; Godef jump key binding
  (local-set-key (kbd "M-.") 'godef-jump))
(add-hook 'go-mode-hook 'my-go-mode-hook)

;;------------------------------------------------------------------------------
;; Python
;;-----------------------------------------------------------------------------


;;---------------------------------------------------------------------------
;; C/C++
;;-----------------------------------------------------------------------------

(load-file "~/.emacs.d/lisp/google-c-style.el")

(setq-default flycheck-clang-language-standard "c++11"
	      flycheck-gcc-language-standard "c++11")

(add-hook 'c-mode-common-hook 'google-set-c-style)

;;-----------------------------------------------------------------------------
;; Keybindings
;;-----------------------------------------------------------------------------

(winner-mode 1)

;; smart window switch
(when (fboundp 'windmove-default-keybindings)
  (windmove-default-keybindings))

(bind-key "C-w" 'kill-region-or-backward-word)
(bind-key "C-a" 'back-to-indentation-or-beginning-of-line)
(bind-key "C-7" 'comment-or-uncomment-current-line-or-region)
(bind-key "C-6" 'linum-mode)
(bind-key "M-g" 'goto-line)
(bind-key "C-o" 'open-line-below)
(bind-key "C-S-o" 'open-line-above)
(bind-key "M-j" 'join-line-or-lines-in-region)
(bind-key "M-w" 'kill-region-or-thing-at-point)
(bind-key "C-S-k" 'kill-whole-line)
(bind-key "C-c g" 'google)
(bind-key "C-S-y" 'copy-line)
(bind-key "C-x y" 'copy-line)
(bind-key "C-," 'previous-buffer)
(bind-key "C-." 'next-buffer)
(global-set-key (kbd "C-x b") 'bs-show)
(global-set-key (kbd "C-x C-b") 'ido-switch-buffer)

(bind-key "C-x '" 'projectile-find-file)
(bind-key "C-'" 'projectile-find-file)
(bind-key "C-x \"" 'projectile-find-file-in-directory)
(bind-key "C-x t" 'fzf)
(bind-key "C-x C-'" 'helm-cmd-t)
(bind-key "C-x n" 'new-frame)
(bind-key "C-q" 'other-window)

(setq aw-scope 'frame)
(bind-key "C-<tab>" 'ace-window)

(bind-key "C-c i" 'helm-swoop)
(bind-key "M-i" 'helm-imenu)
(bind-key "M-s o" 'ido-occur)
(bind-key "C-x g" 'magit-status)
