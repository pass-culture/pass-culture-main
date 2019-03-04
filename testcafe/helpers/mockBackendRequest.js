/* eslint no-console: 0 */

import { RequestMock } from 'testcafe'

import { API_URL } from '../../src/utils/config'

const API_URL_WITHOUT_TRAILING_SLASH = API_URL.replace(/\/$/, '')

function initMockResponse(req, res) {
  console.log(`Mocking call to ${req.method} ${req.path}`)
  res.headers['access-control-allow-origin'] = req.headers.referer
    .split('/')
    .slice(0, 3)
    .join('/')
  res.headers['access-control-allow-credentials'] = 'true'
  res.headers['access-control-allow-headers'] =
    'appname, appversion, content-type, x-request-id'
  res.headers['access-control-allow-methods'] =
    'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT'
}

export const mockBackendRequest = options => {
  const url = API_URL_WITHOUT_TRAILING_SLASH + options.url
  return RequestMock()
    .onRequestTo({ method: 'OPTIONS', url })
    .respond((req, res) => {
      initMockResponse(req, res)
      res.headers.allow = 'PUT, HEAD, OPTIONS, GET'
      res.headers.vary = 'Origin'
      res.statusCode = '200'
    })
    .onRequestTo({ method: 'PUT', url })
    .respond((req, res) => {
      initMockResponse(req, res)
      res.headers['content-type'] =
        options.responseContentType || 'application/json'
      res.statusCode = options.responseStatusCode || 200
      res.setBody(options.responseBody || '')
    })
}
