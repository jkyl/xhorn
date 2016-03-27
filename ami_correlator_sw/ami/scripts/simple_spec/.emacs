;; .emacs

;; uncomment this line to disable loading of "default.el" at startup
;; (setq inhibit-default-init t)

;; Changing fonts, as is done below, from an already running emacs
;; session in some window managers causes an unreasonable hang. This
;; is a fix.
(modify-frame-parameters nil '((wait-for-wm . nil)))

;; turn on font-lock mode
(when (fboundp 'global-font-lock-mode)
  (global-font-lock-mode t))

;; turn on auto-fill-mode for line breaking by default
(setq-default auto-fill-function 'do-auto-fill)

;; Goto-line short-cut key
(global-set-key "\C-l" 'goto-line)

;; enable visual feedback on selections
;(setq transient-mark-mode t)

;; default to better frame titles
(setq frame-title-format
      (concat  "%b - emacs@" system-name))

;; default window size (in units of characters/lines)
(setq default-frame-alist '(
               (width . 120)
                (height . 70) ))

;; default fill column
(setq-default fill-column 80)

;; disable system beep
;;(setq visible-bell t)

(custom-set-variables
  ;; custom-set-variables was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
 '(case-fold-search t)
 '(current-language-environment "English")
 '(global-font-lock-mode t nil (font-lock))
 '(inhibit-startup-screen t)
 '(show-paren-mode t nil (paren))
 '(text-mode-hook (quote (turn-on-auto-fill text-mode-hook-identify)))
 '(transient-mark-mode t))

(set-background-color "black")
(set-foreground-color "dark grey")
(set-face-foreground font-lock-comment-face"Red")
(set-face-foreground font-lock-string-face"Dark Cyan")
(set-face-foreground font-lock-keyword-face"Blue1")
(set-face-foreground font-lock-function-name-face"Orange")
(set-face-foreground font-lock-variable-name-face "Magenta")
(set-face-foreground font-lock-reference-face  "Green1")

;; Use fixed width font, which under Ubuntu seems to not be the default
(set-face-font 'default' "6x13")


;;; Matlab-mode setup: 
  
;; Add local lisp folder to load-path 
;;(setq load-path (append load-path (list "~/.matlab"))) 
 
;; Set up matlab-mode to load on .m files 
;;(autoload 'matlab-mode "matlab" "Enter MATLAB mode." t) 
;;(setq auto-mode-alist (cons '("\\.m\\'" . matlab-mode) auto-mode-alist)) 
;;(autoload 'matlab-shell "matlab" "Interactive MATLAB mode." t) 
 
;; Customization: 
;;(setq matlab-verify-on-save-flag nil) ; turn off auto-verify on save 
;;(defun my-matlab-mode-hook () 
;;  (setq fill-column 90))		; where auto-fill should wrap 
;;(add-hook 'matlab-mode-hook 'my-matlab-mode-hook) 
;;(defun my-matlab-shell-mode-hook () 
;;  '()) 
;;(add-hook 'matlab-shell-mode-hook 'my-matlab-shell-mode-hook) 
 
;; Turn off Matlab desktop 
;;(setq matlab-shell-command-switches '("-nojvm")) 
 
;;(custom-set-faces
  ;; custom-set-faces was added by Custom.
  ;; If you edit it by hand, you could mess it up, so be careful.
  ;; Your init file should contain only one such instance.
  ;; If there is more than one, they won't work right.
;; )
