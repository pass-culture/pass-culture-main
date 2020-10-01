#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division
import sys
import os
import json
import collections
import logging
import time
import re
from urlparse import urlparse, parse_qs
from StringIO import StringIO
import requests
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor

reload(sys)
sys.setdefaultencoding('utf8')

WE_TRANSFER_API_URL = "https://www.wetransfer.com/api/v1/transfers"
DOWNLOAD_URL_PARAMS_PREFIX = "downloads/"
CHUNK_SIZE_U = 5242880
CHUNK_SIZE_D = 1024


class WeTransfer(object):

    def __init__(self,
                 sender='',
                 receivers='',
                 message='',
                 username=None,
                 password=None,
                 channel='',
                 expire_in='',
                 progress=True, 
                 deliverypassword=None):

        self.sender = sender
        self.receivers = receivers
        self.message = message
        self.username = username
        self.password = password
        self.channel = channel
        self.expire_in = expire_in
        self.progress = progress
        self.deliverypassword = deliverypassword
        
        self.session = requests.Session()

        if self.username and password:
            self._get_authenticity_token()
            self.login()

    def _get_authenticity_token(self):
        resp = self.session.get("https://www.wetransfer.com/signin")

        match = re.search(r'<meta name="csrf-token" content="(.*)" />', resp.text)
        if match.group(1):
            self.authenticity_token = match.group(1)

    def login(self):
        dataLogin = {
            "utf8": r'%E2%9C%93',
            "authenticity_token": self.authenticity_token,
            "user[email]": self.username,
            "user[password]": self.password,
            "user[remember_me]": "0",
            "commit": "Connexion"}

        r = self.session.post("https://www.wetransfer.com/users/sign_in",
                              data=dataLogin)

    def _get_transfer_id(self):
        dataTransferId = {
            "channel": self.channel,
            "expire_in": self.expire_in,
            "from": self.sender,
            "message": self.message,
            "pw": self.deliverypassword,
            "to[]": self.receivers,
            "utype": "js"}
        if self.sender:
            dataTransferId["ttype"] = "1"
        else:
            dataTransferId["ttype"] = "4"
        r = self.session.post(WE_TRANSFER_API_URL, data=dataTransferId)

        while(r.status_code != 200):
            time.sleep(2)
            r = self.session.post(WE_TRANSFER_API_URL, data=dataTransferId)

        response_data = json.loads(r.content)

        try:
            return response_data["transfer_id"]
        except KeyError as e:
            raise Exception('Error', e)

    def _get_file_objectid(self, filename, filesize):
        dataFileObjectId = {
            "chunked": "true",
            "direct":   "false",
            "filename":    filename,
            "filesize": filesize}

        r = self.session.post(
            (WE_TRANSFER_API_URL + "/{0}/file_objects")
            .format(self.transfer_id),
            data=dataFileObjectId)
        response_data = json.loads(r.content)

        return response_data

    def _get_chunk_info_for_upload(self, fileObjectId, chunkNumber,
                                   chunkSize=CHUNK_SIZE_U):
        dataChunk = {
            "chunkNumber": chunkNumber,
            "chunkSize":  chunkSize,
            "retries": "0"}

        r = self.session.put(
            (WE_TRANSFER_API_URL + "/{0}/file_objects/{1}")
            .format(self.transfer_id, fileObjectId),
            data=dataChunk)

        return json.loads(r.content)

    def _draw_progressbar(self, percent, barLen=40):
        progress = ""
        for i in range(barLen):
            if i < int(barLen * percent):
                progress += "="
            else:
                progress += " "
        sys.stdout.write("\r[ %s ] %.2f%%" % (progress, percent * 100))
        sys.stdout.flush()

    def _create_callback(self, previousChunks, fileSize):
        def callback(monitor):
            self._draw_progressbar(
                float(previousChunks + monitor.bytes_read)/float(fileSize))
        return callback

    def _upload_chunk(self, chunkInfo, filename, dataBin, fileType,
                      chunkNumber, fileSize):
        url = chunkInfo["url"]

        dataChunkUpload = collections.OrderedDict()
        for k, v in chunkInfo["fields"].items():
            dataChunkUpload[k] = v

        dataChunkUpload["file"] = (filename, dataBin, fileType)

        e = MultipartEncoder(fields=dataChunkUpload)
        if self.progress:
            e = MultipartEncoderMonitor(e,
                                    self._create_callback(
                                        chunkNumber*CHUNK_SIZE_U, fileSize))
        r = self.session.post(url,
                              data=e,
                              headers={'Content-Type': e.content_type})

    def _finalize_chunks(self, fileObjectId, partCount):
        dataFinalizeChunk = {
            "finalize_chunked": "true",
            "part_count": partCount}
        r = self.session.put((WE_TRANSFER_API_URL +
            "/{0}/file_objects/{1}").format(self.transfer_id, fileObjectId),
                             data=dataFinalizeChunk)

    def _finalize_transfer(self):
        r = self.session.put((WE_TRANSFER_API_URL +
            "/{0}/finalize").format(self.transfer_id))
        response = json.loads(r.content)
        url = response["shortened_url"]
        return url

    def _cancel_transfer(self):
        print("Cancelling transfer")
        r = self.session.put((WE_TRANSFER_API_URL +
            "/{0}/cancel").format(self.transfer_id))

    def _read_in_chunks(self, file_object, chunk_size=CHUNK_SIZE_U):
        """Lazy function (generator) to read a file piece by piece.
        Default chunk size: 5Mo."""
        while True:
            data = file_object.read(chunk_size)
            if not data:
                break
            yield data

    def uploadFile(self, fileToUpload):
        self.transfer_id = self._get_transfer_id()
        logging.info("Transfer_id: %s" % self.transfer_id)

        logging.debug("Upload file: %s" % fileToUpload) 
        with open(fileToUpload, 'rb') as f:
            fileMimeType = "application/octet-stream"
            fileSize = os.path.getsize(fileToUpload)
            fileName = os.path.basename(fileToUpload)

            dataFileObjectId = self._get_file_objectid(fileName, fileSize)
            if "url" in dataFileObjectId:
                self._upload_chunk(dataFileObjectId, fileName,
                                   f.read(fileSize), fileMimeType, 0, fileSize)
                self._finalize_chunks(dataFileObjectId["file_object_id"], 1)
            else:
                chunkNumber = 1

                for piece in self._read_in_chunks(f):
                    chunkInfo = self._get_chunk_info_for_upload(
                        dataFileObjectId["file_object_id"],
                        chunkNumber,
                        sys.getsizeof(piece))
                    self._upload_chunk(chunkInfo, fileName, piece,
                                       fileMimeType, chunkNumber-1, fileSize)
                    chunkNumber = chunkNumber + 1

                self._finalize_chunks(
                    dataFileObjectId["file_object_id"], chunkNumber - 1)
        print '\n'
        return self._finalize_transfer()

    def uploadDir(self, top, recursive=False):
        """
        descend the directory tree rooted at top,
        calling the upload function for each regular file
        """

        for root, dirs, files in os.walk(top):
            if not recursive:
                while len(dirs) > 0:
                    dirs.pop()

            for name in files:
                print("Upload file : " + os.path.abspath(
                    os.path.join(root, name)))
                self.uploadFile(os.path.abspath(os.path.join(root, name)))

    def download(self, url, destination=None):
	url = self._extract_url_redirection(url)
        [file_id, recipient_id, security_hash] = self._extract_params(url)
        url = "https://www.wetransfer.com/api/v1/transfers/{0}/"\
            "download?recipient_id={1}&security_hash={2}&password=&ie=false"\
            .format(file_id, recipient_id, security_hash)
        r = requests.get(url)
        download_data = json.loads(r.content)

        print "Downloading {0}...".format(url)
        if 'direct_link' in download_data:
            content_info_string = parse_qs(
                urlparse(download_data['direct_link']).query)
            file_name_data = content_info_string['filename']
            file_name = file_name_data[0]
            r = requests.get(download_data['direct_link'], stream=True)
        else:
            file_name = download_data['fields']['filename']
            r = requests.post(
                download_data['formdata']['action'],
                data=download_data["fields"],
                stream=True
                )
        file_size = int(r.headers["Content-Length"])

        if destination:
            if os.path.isdir(destination):
                file_name = os.path.join(destination, file_name)

        with open(file_name, 'wb') as output_file:
            counter = 0
            for chunk in r.iter_content(chunk_size=CHUNK_SIZE_D):
                if chunk:
                    output_file.write(chunk)
                    output_file.flush()
                    if self.progress:
                        self._draw_progressbar((counter * CHUNK_SIZE_D) * 1.0/file_size)
                    counter += 1
        # sys.stdout.write('\r100% {0}/{1}\n'.format(file_size, file_size))
        print "\nFinished! {0}\n".format(file_name)

    def _extract_params(self, url):
        """
            Extracts params from url
            """
        params = url.split(DOWNLOAD_URL_PARAMS_PREFIX)[1].split('/')
        [file_id, recipient_id, security_hash] = ['', '', '']
        if len(params) > 2:
            # The url is similar to
            # https://www.wetransfer.com/downloads/XXXXXXXXXX/YYYYYYYYY/ZZZZZZZZ
            [file_id, recipient_id, security_hash] = params
        else:
            # The url is similar to https://www.wetransfer.com/downloads/XXXXXXXXXX/ZZZZZZZZ
            # In this case we have no recipient_id
                [file_id, security_hash] = params

        return [file_id, recipient_id, security_hash]

    def _extract_url_redirection(self, url):
    	"""
        Follow the url redirection if necesary
   	"""
    	return requests.get(url).url
