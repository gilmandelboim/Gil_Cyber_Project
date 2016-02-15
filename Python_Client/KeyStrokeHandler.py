#!/usr/bin/env python

import win32con, win32api, win32gui
from ctypes import *


class KeyboardHook:
    """
    To install the hook, call the (gasp!) installHook() function.
    installHook() takes a pointer to the function that will be called
    after a keyboard event.  installHook() returns True if everything
    was successful, and False if it failed
    Note:  I've also provided a function to return a valid function pointer
    
    To make sure the hook is actually doing what you want, call the
    keepAlive() function
    Note:  keepAlive() doesn't return until kbHook is None, so it should
    be called from a separate thread
    
    To uninstall the hook, call uninstallHook()    

    """
    # Capital letters
    vkeys_list = [ 65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90 ]

    def __init__(self, wordsHandler):
        self.wordsHandler = wordsHandler
        self.user32     = windll.user32
        self.kbHook     = None
        self.writtin_string = ""
    
    def installHook(self, pointer):
        self.kbHook = self.user32.SetWindowsHookExA(
                              win32con.WH_KEYBOARD_LL,
                              pointer,
                              win32api.GetModuleHandle(None),
                              0 # this specifies that the hook is pertinent to all threads
        )
        return self.kbHook != None
    
    def keepAlive(self):
        if self.kbHook is None:
            return
        msg = win32gui.GetMessage(None, 0, 0)
        while msg and self.kbHook is not None:
            win32gui.TranslateMessage(byref(msg))
            win32gui.DispatchMessage(byref(msg))
            msg = win32gui.GetMessage(None, 0, 0)
    
    def uninstallHook(self):
        if self.kbHook is None:
            return
        self.user32.UnhookWindowsHookEx(self.kbHook)
        self.kbHook = None

    ##################################################
    # returns a function pointer to the fn paramater #
    # assumes the function takes three params:       #
    # c_int, c_int, and POINTER(c_void_p)            #
    ##################################################
    def getFunctionPointer(self, fn):
        CMPFUNC = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
        return CMPFUNC(fn)

    #############################################
    # Sample function to handle keyboard events #
    #############################################
    def kbEvent(self, nCode, wParam, lParam):
        if wParam is not win32con.WM_KEYDOWN: # It just occured to me that I should aso be checking for WM_SYSKEYDOWN as well
            return self.user32.CallNextHookEx(self.kbHook, nCode, wParam, lParam)
        if lParam[0] in self.vkeys_list:
            if chr(lParam[0]) == ' ':
                self.writtin_string = ""
            else:
                self.writtin_string += chr(lParam[0])
                if self.wordsHandler.common_word_and_site(self.writtin_string) :
                    self.writtin_string = ""
        return self.user32.CallNextHookEx(self.kbHook, nCode, wParam, lParam)

    def start(self):
        pointer = self.getFunctionPointer(self.kbEvent)
        self.installHook(pointer)
        #keyboardHook.uninstallHook()
        self.keepAlive()

