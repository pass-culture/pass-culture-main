import 'regenerator-runtime/runtime'
import { expect, vi } from 'vitest'
import * as matchers from 'vitest-axe/matchers'
import '@testing-library/jest-dom'
import createFetchMock from 'vitest-fetch-mock'
import 'vitest-canvas-mock'

expect.extend(matchers)

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()
fetchMock.mockResponse(req => {
  // eslint-disable-next-line
  console.error(`
  ----------------------------------------------------------------------------
  /!\\ UNMOCKED FETCH CALL TO :  [${req.method}] ${req.url}
  ----------------------------------------------------------------------------
  `)

  // We do not await this Promise so that Jest considers it as
  // an unhandled rejection and thus fails the test
  // (otherwise the console.error will appear but not fail the test)
  void Promise.reject('Unmocked fetch call')

  // And now return a Promise so that fetchMock is happy
  return Promise.reject('Unmocked fetch call')
})

/* BELOW WE HANDLE WARNINGS AND ERRORS THROWN INSIDE THE TESTS */

// DO NOT ADD ERRORS TO THIS LIST!
// We should remove it progressively
const acceptableErrors = [
  // This error exists in the following test:
  // src/pages/OfferIndividualWizard/Confirmation/__specs__/Confirmation.spec.tsx
  // It exists because we click on an anchor tag (<a>) and assert that the tracking
  // is called.
  // However Jest doesn't support navigation changes and we shouldn't click on links in tests
  // Furthermore, we shouldn't have to manually track page changes as Google Analytics
  // should do this out of the box. So the real good solution here is:
  // - check why we manually track page changes with the data team
  // - remove all trackers used to track page changes
  // - remove the offending test
  {
    error: 'Error: Not implemented: navigation (except hash changes)',
    files: [''],
  },
  // This is added because `orejim` uses React 17 internally.
  // We'll wait for the library update to remove this.
  {
    error:
      "Warning: ReactDOM.render is no longer supported in React 18. Use createRoot instead. Until you switch to the new API, your app will behave as if it's running React 17. Learn more: https://reactjs.org/link/switch-to-createroot",
    files: [''],
  },
]

const findErrorSourceFile = (...data: any[]) => {
  let fileMatching: string | null = null
  for (let i = 0; i < data.length; i++) {
    const item = data[i]
    if (!(typeof item === 'string')) {
      return false
    }

    const isSourceFileRegexp = new RegExp('pro/src')
    const lines = item.split('\n')
    for (let j = 0; j < lines.length; j++) {
      if (isSourceFileRegexp.test(lines[j])) {
        fileMatching = lines[j]
        break
      }
    }
    if (fileMatching !== null) {
      break
    }
  }

  const extractFilenameRegexp = new RegExp('pro/src/(.*):.*:')
  return fileMatching?.match(extractFilenameRegexp)?.[1]
}

const isErrorInAllowList = (...data: any[]) => {
  const cleanedError = data[0].split('\n')[0]
  // When this message happens, it is always because there is another console.error that is more relevant
  if (cleanedError.includes('The above error occurred in')) {
    return true
  }

  const errorSourceFile = findErrorSourceFile(...data)

  return acceptableErrors.some(
    possibleError =>
      possibleError.error === cleanedError &&
      possibleError.files.includes(errorSourceFile || '')
  )
}

// Flag console.warn and console.error as failed tests
const originalWarn = global.console.warn
global.console.warn = (message, ...args) => {
  originalWarn(`Already caught: ${message}`, ...args)

  if (!isErrorInAllowList(message, ...args)) {
    throw message
  }
}

const originalError = global.console.error
global.console.error = (message, ...args) => {
  originalError(`Already caught: ${message}`, ...args)

  if (!isErrorInAllowList(message, ...args)) {
    throw message
  }
}
