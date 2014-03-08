#import library to do http requests:
import urllib2
#threads used to test the urls
from threading import Thread
import os
import sys
#import easy to use xml parser called minidom:
from xml.dom.minidom import parseString
#'C:\Program Files\Lenovo\Lenovo Solution Center\lscUrls.xml'

class UrlCheck(object):
	tag = ''
	url = ''
	requestUrl = ''
	code = 0

	def __init__(self, tag, url):
		self.tag = tag
		self.url = url

	def redirected(self):
		return self.url != self.requestUrl

class UrlValidator(object):
	urlXmlPath = ''
	resultCsvPath = ''

	def __init__(self, urlXmlPath, resultCsvPath):
		self.urlXmlPath = urlXmlPath

		if len(resultCsvPath) == 0:
			self.resultCsvPath = os.getcwd() + '\\urlCheck.csv'
		else:
			self.resultCsvPath = resultCsvPath
		print 'Path to csv file: ' + self.resultCsvPath

	def validate(self):
		# check if target file is free to use
		if self.isFileOpen(self.resultCsvPath):
			sys.exit()
		# read urls from the xml file
		urlCheckList = self.readLscUrls(self.urlXmlPath)
		# test the urls
		self.checkUrl(urlCheckList)
		# write the results to a csv
		finalUrlCheckList = self.generateReport(urlCheckList)
		print 'Number of URLs: %s, Processed: %s' % (len(urlCheckList), len(finalUrlCheckList))

	def checkUrl(self, urlCheckList):
		finalUrlCheckList = []
		for urlCheck in urlCheckList:
			print 'testing url: %s' % urlCheck.url
			try:
				response = urllib2.urlopen(urlCheck.url)
				urlCheck.requestUrl = response.geturl()
				urlCheck.code = response.code
				if urlCheck.redirected:
					urlCheck.code = 301
				response.close()
				finalUrlCheckList.append(urlCheck)
			except urllib2.URLError as e:
				#failed to reach server
				print 'URLError: %s' % e.reason
				if str(e.reason).lower() == 'not found':
					urlCheck.code = 404
				else:
					urlCheck.code = e.reason
			except urllib2.HTTPError as e:
				urlCheck.code = e.code
			print 'response code: %s' % ('301/302' if urlCheck.requestUrl != urlCheck.url else urlCheck.code)
			return finalUrlCheckList

	def testUrlThreaded(self, urlCheckList, numberOfThreads):
		# Start the threads, passing a list for each one to process
		for i in xrange(0, len(urlCheckList), numberOfThreads):
			t = Thread(target=self.checkUrl, args=(urlCheckList[i:i+numberOfThreads]))
			#self.threadList.append(t)
			yield t.start()

	def generateReport(self, urlCheckList):
		try:
			f = open(self.resultCsvPath, 'w')
			f.write('Tag,Url,HTTP Code,Redirected,New Url\n')
			for urlCheck in urlCheckList:
				print '%s, %s, %s, %s\n' % (urlCheck.tag, urlCheck.url, urlCheck.code, urlCheck.requestUrl if urlCheck.redirected() else '')
				f.write('%s, %s, %s, %s\n' % (urlCheck.tag, urlCheck.url, urlCheck.code, urlCheck.requestUrl if urlCheck.redirected() else ''))
		except IOError as err:
			print 'Error: Could\'t open or create file. Reason: ' + err.strerror
			sys.exit()
		else:
			f.close()

	def isFileOpen(self, filePath):
		isOpen = False
		try:
			f = open(filePath, 'w')
			f.close()
		except IOError:
			print "File @ %s is open, please close it." % filePath
			isOpen = True
		return isOpen

	def readLscUrls(self, xmlPath):
		try:
			#open the xml file for reading:
			f = open(xmlPath,'r')
			#convert to string:
			data = f.read()
		except IOError as err:
			print 'Error: Could\'t open or create file. Reason: ' + err.strerror
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
				if tagUrl.find("http://") != -1 or tagUrl.find("https://") != -1:
					urlList.append(UrlCheck(urlNode.nodeName.strip(), tagUrl))
		return urlList

	def printUrlsFromDict(self, urlList):
		for urlCheck in urlList:
			print(urlCheck.tag, "-", urlCheck.url)

	def printRequestResult(self, response):
		print 'RESPONSE:', response
		print 'URL     :', response.geturl()
		print 'CODE    :', response.code
		headers = response.info()
		print 'DATE    :', headers['date']
		print 'HEADERS :'
		print '---------'
		print headers



#urlValidator = UrlValidator('C:\Program Files\Lenovo\Lenovo Solution Center\lscUrls.xml', 'C:\Users\saotfern\Desktop\urlCheck.csv')
#urlValidator.validate('C:\Users\saotfern\Desktop\lscUrls_short.xml')
urlValidator = UrlValidator('C:\Program Files\Lenovo\Lenovo Solution Center\lscUrls.xml', '')
urlValidator.validate()

'''
TODO:
. Receive command line arguments - Path to xml and csv
. Return usage in case no arguments are passed
. Generate executable
. Add argument -D for debug - it'll print each url to the shell
'''