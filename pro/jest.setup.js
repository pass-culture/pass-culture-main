import 'regenerator-runtime/runtime'

import fetch from 'jest-fetch-mock'

global.fetch = fetch
const originalGetComputedStyle = window.getComputedStyle

// required for setting 0 values and to avoid warnings like "NAN is not a number" within jest tests
// getComputedStyle is used by react calendar and cause this issue
const getComputedStyle = (...args) => {
  const cssStyleDeclaration = originalGetComputedStyle(...args)
  cssStyleDeclaration.setProperty('padding-left', 0)
  cssStyleDeclaration.setProperty('padding-right', 0)
  cssStyleDeclaration.setProperty('padding-top', 0)
  cssStyleDeclaration.setProperty('padding-bottom', 0)
  cssStyleDeclaration.setProperty('margin-left', 0)
  cssStyleDeclaration.setProperty('margin-right', 0)
  cssStyleDeclaration.setProperty('margin-top', 0)
  cssStyleDeclaration.setProperty('margin-bottom', 0)
  cssStyleDeclaration.setProperty('border-left-width', 0)
  cssStyleDeclaration.setProperty('border-right-width', 0)
  cssStyleDeclaration.setProperty('border-top-width', 0)
  cssStyleDeclaration.setProperty('border-bottom-width', 0)

  return cssStyleDeclaration
}

Object.defineProperty(window, 'getComputedStyle', {
  value: getComputedStyle,
})

Object.defineProperty(window, 'scrollTo', {
  value: () => null,
})

fetch.mockResponse(req => {
  const msg = `
----------------------------------------------------------------------------
/!\\ UNMOCKED FETCH CALL TO :  ${req.url}
----------------------------------------------------------------------------
` // FIX ME
  // eslint-disable-next-line
  console.error(msg)
  return Promise.reject(new Error(msg))
})

jest.mock('tracking/mediaCampaignsTracking')
