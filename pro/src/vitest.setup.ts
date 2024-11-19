import 'regenerator-runtime/runtime'
import { expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import * as matchers from 'vitest-axe/matchers'
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

/* BELOW WE HANDLE WARNINGS AND ERRORS THROWN INSIDE THE TESTS */

// DO NOT ADD ERRORS TO THIS LIST!
// We should remove it progressively
const acceptableErrors = [
  // This is added because `orejim` uses React 17 internally.
  // We'll wait for the library update to remove this.
  {
    error:
      "Warning: ReactDOM.render is no longer supported in React 18. Use createRoot instead. Until you switch to the new API, your app will behave as if it's running React 17. Learn more: https://reactjs.org/link/switch-to-createroot",
    files: [''],
  },
  {
    error:
      '⚠️ React Router Future Flag Warning: React Router will begin wrapping state updates in `React.startTransition` in v7. You can use the `v7_startTransition` future flag to opt-in early. For more information, see https://reactrouter.com/v6/upgrading/future#v7_starttransition.',
    files: [''],
  },
  {
    error:
      '⚠️ React Router Future Flag Warning: Relative route resolution within Splat routes is changing in v7. You can use the `v7_relativeSplatPath` future flag to opt-in early. For more information, see https://reactrouter.com/v6/upgrading/future#v7_relativesplatpath.',
    files: [''],
  },
  {
    error:
      '⚠️ React Router Future Flag Warning: The persistence behavior of fetchers is changing in v7. You can use the `v7_fetcherPersist` future flag to opt-in early. For more information, see https://reactrouter.com/v6/upgrading/future#v7_fetcherpersist.',
    files: [''],
  },
  {
    error:
      '⚠️ React Router Future Flag Warning: Casing of `formMethod` fields is being normalized to uppercase in v7. You can use the `v7_normalizeFormMethod` future flag to opt-in early. For more information, see https://reactrouter.com/v6/upgrading/future#v7_normalizeformmethod.',
    files: [''],
  },
  {
    error:
      '⚠️ React Router Future Flag Warning: `RouterProvider` hydration behavior is changing in v7. You can use the `v7_partialHydration` future flag to opt-in early. For more information, see https://reactrouter.com/v6/upgrading/future#v7_partialhydration.',
    files: [''],
  },
  {
    error:
      '⚠️ React Router Future Flag Warning: The revalidation behavior after 4xx/5xx `action` responses is changing in v7. You can use the `v7_skipActionErrorRevalidation` future flag to opt-in early. For more information, see https://reactrouter.com/v6/upgrading/future#v7_skipactionerrorrevalidation.',
    files: [''],
  },
  // Radix-ui updates wants us to use `DialogTitle` that always adds a `h2`
  // RGAA requires the title to be a `h1`
  // All our dilogs have titles
  {
    error:
      '`DialogContent` requires a `DialogTitle` for the component to be accessible for screen reader users.',
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
    (possibleError) =>
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
