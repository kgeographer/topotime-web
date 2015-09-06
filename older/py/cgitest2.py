#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys

def cgime(foo):
	if len(foo) > 3:
		return 'you entered '+foo
	else:
		return 'need bigger input' 
		
if len(sys.argv[1]) > 3:
	print 'you entered '+str(sys.argv[1])
else:
	print 'need bigger input' 
