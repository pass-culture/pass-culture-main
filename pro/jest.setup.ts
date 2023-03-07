import 'regenerator-runtime/runtime'
import fetchMock from 'jest-fetch-mock'

import '@testing-library/jest-dom'
import acceptableErrors from './jestErrorsAllowList'
import { toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

fetchMock.enableMocks()

fetchMock.mockResponse(req => {
  // eslint-disable-next-line
  console.error(`
  ----------------------------------------------------------------------------
  /!\\ UNMOCKED FETCH CALL TO :  ${req.url}
  ----------------------------------------------------------------------------
  `)

  // We do not await this Promise so that Jest considers it as
  // an unhandled rejection and thus fails the test
  // (otherwise the console.error will appear but not fail the test)
  void Promise.reject('Unmocked fetch call')

  // And now return a Promise so that fetchMock is happy
  return Promise.reject('Unmocked fetch call')
})

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
