import 'regenerator-runtime/runtime'
import { expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import * as matchers from 'vitest-axe/matchers'
import failOnConsole from 'vitest-fail-on-console'
import createFetchMock from 'vitest-fetch-mock'
import 'vitest-canvas-mock'

expect.extend(matchers)
const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()
fetchMock.mockResponse((req) => {
  // eslint-disable-next-line
  console.error(`
  ----------------------------------------------------------------------------
  /!\\ UNMOCKED FETCH CALL TO :  [${req.method}] ${req.url}
  ----------------------------------------------------------------------------
  `)

  // We do not await this Promise so that Vitest considers it as
  // an unhandled rejection and thus fails the test
  // (otherwise the console.error will appear but not fail the test)
  void Promise.reject('Unmocked fetch call')

  // And now return a Promise so that fetchMock is happy
  return Promise.reject('Unmocked fetch call')
})

// Mock the ResizeObserver for Charts
class ResizeObserver {
  observe() {}

  unobserve() {}

  disconnect() {}
}

window.ResizeObserver = ResizeObserver

// Fail on console errors and warnings
// https://github.com/thomasbrodusch/vitest-fail-on-console#readme
failOnConsole()
