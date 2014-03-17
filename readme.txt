# To generate a new exe, run:
python setup.py py2exe

# Fix - Single threaded
Traceback (most recent call last):
  File "checkUrl.py", line 294, in <module>
    main()
  File "checkUrl.py", line 283, in main
    urlValidator.validate()
  File "checkUrl.py", line 85, in validate
    finalUrlCheckList = self.checkUrls(urlCheckList)
  File "checkUrl.py", line 98, in checkUrls
    finalUrlCheckList.extend(self.checkSingleUrl_Lang(urlCheck))
  File "checkUrl.py", line 137, in checkSingleUrl_Lang
    urlCheckList.append(self.checkSingleUrl(langUrlCheck))
  File "checkUrl.py", line 144, in checkSingleUrl
    response = urllib2.urlopen(urlCheck.url)
  File "c:\Python27\lib\urllib2.py", line 127, in urlopen
    return _opener.open(url, data, timeout)
  File "c:\Python27\lib\urllib2.py", line 404, in open
    response = self._open(req, data)
  File "c:\Python27\lib\urllib2.py", line 422, in _open
    '_open', req)
  File "c:\Python27\lib\urllib2.py", line 382, in _call_chain
    result = func(*args)
  File "c:\Python27\lib\urllib2.py", line 1214, in http_open
    return self.do_open(httplib.HTTPConnection, req)
  File "c:\Python27\lib\urllib2.py", line 1187, in do_open
    r = h.getresponse(buffering=True)
  File "c:\Python27\lib\httplib.py", line 1045, in getresponse
    response.begin()
  File "c:\Python27\lib\httplib.py", line 409, in begin
    version, status, reason = self._read_status()
  File "c:\Python27\lib\httplib.py", line 365, in _read_status
    line = self.fp.readline(_MAXLINE + 1)
  File "c:\Python27\lib\socket.py", line 476, in readline
    data = self._sock.recv(self._rbufsize)
socket.error: [Errno 10054] An existing connection was forcibly closed by the re
mote host