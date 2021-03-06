#!/usr/bin/env python
#import library to do http requests:
import urllib2
#threads used to test the urls
import Queue, threading
import os, sys
from optparse import OptionParser
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
# Benchmark for debug purposes
import time

class UrlCheck(object):
	tag = ''
	url = ''
	requestUrl = ''
	code = 0

	def __init__(self, tag, url):
		self.tag = tag
		self.url = url
		self.requestUrl = url

	def redirected(self):
		return self.url != self.requestUrl

	def setUrl(self, url):
		self.url = url
		self.requestUrl = url

class UrlValidator(object):
	_urlXmlPath = ''
	_resultCsvPath = ''
	_machineSerialNumber = ''
	_debugMode = False
	_threadResult = []
	useThreads = False
	_langDict = {
	'DK': 'en',
	'DE': 'de',
	'US': 'en',
	'ES': 'es',
	'FI': 'en',
	'FR': 'fr',
	'IT': 'it',
	'JP': 'ja',
	'KR': 'ko',
	'NO': 'en',
	'NL': 'en',
	'PL': 'pl',
	'BR': 'pt',
	'PT': 'pt',
	'RU': 'ru',
	'SE': 'en',
	'CN': 'zh',
	'HK': 'zh',
	'TW': 'zh'
	}

	def enableDebug(self):
		self._debugMode = True

	def __init__(self, urlXmlPath, resultCsvPath, serialNumber):
		self._urlXmlPath = urlXmlPath
		self._machineSerialNumber = serialNumber
		
		if len(resultCsvPath) == 0:
			self._resultCsvPath = os.getcwd() + '\\urlCheck.csv'
		else:
			self._resultCsvPath = resultCsvPath

		if self._debugMode:
			print 'Path to input file: %s' % self._urlXmlPath
			print 'Path to output file: %s' % self._resultCsvPath

	def validate(self):
		if self.checkInputFile(self._urlXmlPath) == False:
			sys.exit()
		# read urls from the xml file
		urlCheckList = self.readLscUrls(self._urlXmlPath)
		# test the urls
		if self.useThreads:
			finalUrlCheckList = self.checkUrls_threaded(urlCheckList)
		else:
			finalUrlCheckList = self.checkUrls(urlCheckList)
		# write the results to a csv
		self.generateReport(finalUrlCheckList)
		if self._debugMode:
			print 'Number of URLs processed: %s' % len(finalUrlCheckList)

	def checkUrls(self, urlCheckList):
		finalUrlCheckList = []
		for urlCheck in urlCheckList:
			# If the url needs serial number, replace {1} by the serial
			if urlCheck.url.find('{1}') != -1 and len(self._machineSerialNumber) > 0:
				urlCheck.setUrl(urlCheck.url.replace('{1}', self._machineSerialNumber))
			if urlCheck.url.find('{0}') != -1:
				finalUrlCheckList.extend(self.checkSingleUrl_Lang(urlCheck))
			else:
				finalUrlCheckList.append(self.checkSingleUrl(urlCheck))
		return finalUrlCheckList

	def checkUrls_threaded(self, urlCheckList):
		# Start the threads, passing a list for each one to process
		q = Queue.Queue()
		for url in urlCheckList:
			q.put(url)
		
		thread_count = 5
		for i in range(thread_count):
			t = threading.Thread(target=worker, args = (q,))
			# Daemon means that this process won't block the main thread.
			# If the main Thread closes, it will also terminate.
			t.daemon = True
			t.start()
		# Block until all the tasks are done
		q.join()
		return self._threadResult

	def worker(self, queue):
		queue_full = True
		while queue_full:
			try:
				# Retrieve first item from Queue and process
				urlList = queue.get(False) # Non blocking
				self._threadResult.extend(self.checkUrls(urlList))
			except Queue.Empty:
				queue_full = False

	def checkSingleUrl_Lang(self, baseUrlCheck):
		urlCheckList = []
		for lang in self._langDict.values():
			# Create a new UrlCheck for the language
			langUrlCheck = UrlCheck(baseUrlCheck.tag + '_' + lang, baseUrlCheck.url.replace('{0}', lang))
			if self._debugMode:
				print '\nTesting language: %s' % lang
			urlCheckList.append(self.checkSingleUrl(langUrlCheck))
		return urlCheckList

	def checkSingleUrl(self, urlCheck):
		if self._debugMode:
			print '\nTesting url: %s' % urlCheck.url
		try:
			response = urllib2.urlopen(urlCheck.url)
			urlCheck.requestUrl = response.geturl()
			urlCheck.code = response.code
			if urlCheck.redirected:
				# Don't know how to differentiate between a 301 and a 302.
				urlCheck.code = 301
			response.close()
		except urllib2.URLError as e:
			#failed to reach server
			if self._debugMode:
				print 'URLError: %s' % e.reason
			if str(e.reason).lower() == 'not found':
				urlCheck.code = 404
			else:
				urlCheck.code = e.reason
		except urllib2.HTTPError as e:
			urlCheck.code = e.code
		if self._debugMode:
			print 'Response code: %s' % urlCheck.code
			if urlCheck.redirected:
				print 'Redirected to: %s' % urlCheck.requestUrl
		return urlCheck

	def generateReport(self, urlCheckList):
		try:
			f = open(self._resultCsvPath, 'w')
			f.write('Tag,Url,HTTP Code,Redirected,New Url\n')
			for urlCheck in urlCheckList:
				#if self._debugMode:
					#print '%s, %s, %s, %s\n' % (urlCheck.tag, urlCheck.url, urlCheck.code, urlCheck.requestUrl if urlCheck.redirected() else '')
				f.write('%s, %s, %s, %s\n' % (urlCheck.tag, urlCheck.url, urlCheck.code, urlCheck.requestUrl if urlCheck.redirected() else ''))
		except IOError as err:
			if self._debugMode:
				print 'Error: Could\'t open or create file. Reason: ' + err.strerror
			sys.exit()
		else:
			f.close()

	def checkInputFile(self, filePath):
		isFileOk = False
		doExist = os.path.exists(filePath)
		isFile = os.path.isfile(filePath)
		
		if doExist and isFile:
			isFileOk = True
		else:
			if self._debugMode:
				print "File '%s' does not exist or isn't a file." % self._urlXmlPath

		return isFileOk

	def checkOutputFile(self, filePath):
		if isFileOk:
			# check if target file is free to use
			if self.isFileOpen(filePath):
				isFileOk = False
				if self._debugMode:
					print "File '%s' is open, please close it." % self._urlXmlPath

	def isFileOpen(self, filePath):
		isOpen = False
		try:
			f = open(filePath, 'w')
			f.close()
		except IOError:
			isOpen = True
		return isOpen

	def readLscUrls(self, xmlPath):
		try:
			#open the xml file for reading:
			f = open(xmlPath,'r')
			#convert to string:
			data = f.read()
		except IOError as err:
			if self._debugMode:
				print 'Error: Could\'t read file. Reason: ' + err.strerror
			sys.exit()
		else:
			#close file because we dont need it anymore:
			f.close()
		#parse the xml you got from the file
		dom = parseString(data)
		urlNodeList = dom.getElementsByTagName('config')[0]
		urlList = []
		for urlNode in urlNodeList.childNodes:
			if urlNode.nodeType == urlNode.ELEMENT_NODE:
				tagUrl = urlNode.toxml().replace('<'+urlNode.nodeName+'>','').replace('</'+urlNode.nodeName+'>','').strip()
				if tagUrl[0:8].find('http://') != -1 or tagUrl[0:8].find('https://') != -1:
					urlList.append(UrlCheck(urlNode.nodeName.strip(), tagUrl))
		return urlList

	def printUrlsFromDict(self, urlList):
		for urlCheck in urlList:
			print(urlCheck.tag, "-", urlCheck.url)


def module_path(local_function):
	import inspect
	''' returns the module path without the use of __file__.  Requires a function defined 
	locally in the module. Won't require if you use "lambda _: None" as param without the quotes.
	from http://stackoverflow.com/questions/729583/getting-file-path-of-imported-module'''
	return os.path.abspath(inspect.getsourcefile(local_function))

def main():
	usage = 'usage: %prog [options] urlsFile machineSerialNumber'
	#outFile = os.path.dirname(os.path.abspath(__file__))
	script_path = module_path(lambda _: None)
	RESULT_FILE_NAME = 'result.csv'
	inFile = ''
	parser = OptionParser(usage=usage, version='%prog 1.0')
	parser.add_option('-v', '--verbose', 
		action='store_true', dest='verbose', default=False, 
		help='shows details about the running requests, will also display other infos about the process[default: %default]')
	parser.add_option('-o', '--output', dest='outputFile', metavar='FILE', 
		default=os.path.join(os.path.dirname(os.path.abspath(script_path)), RESULT_FILE_NAME),
		help='write output to FILE, will write ' + RESULT_FILE_NAME + ' to same path as the program if none is provided.')
	parser.add_option('-t', '--threaded',
		action='store_true', dest='useThreads', default=False,
		help='if set to true will run concurrent requests, it will speed the test.')
	
	(options, args) = parser.parse_args()
	
	if len(args) != 2:
		parser.error('incorrect number of arguments')
	else:
		inFile = args[0]
		serial = args[1]

	# Create the url validator and run the check
	tstart = time.clock()
	urlValidator = UrlValidator(inFile, options.outputFile, serial)
	if options.verbose:
		urlValidator.enableDebug()
	
	urlValidator.validate()
	
	if options.verbose:
		print 'Time spent %s' % (time.clock()-tstart)

if __name__ == "__main__":
	main()

'''
TODO:
. Check an implementation of checkUrl using -> http://docs.python.org/2/library/httplib.html
'''