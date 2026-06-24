import 'regenerator-runtime/runtime'
import axeCore from 'axe-core'
import { expect, vi } from 'vitest'
import '@testing-library/jest-dom/vitest'
import type { JSDOM } from 'jsdom'
import * as matchers from 'vitest-axe/matchers'
import failOnConsole from 'vitest-fail-on-console'
import createFetchMock from 'vitest-fetch-mock'
import 'vitest-canvas-mock'

expect.extend(matchers)

// jsdom cannot compute color contrast (no real layout/paint),
// so axe-core's `color-contrast` rule queries pseudo-element styles and always fails on transparent backgrounds.
// This disables it globally (rather than per-test).
// https://github.com/NickColley/jest-axe/issues/147#issuecomment-1300192415
axeCore.configure({
  rules: [{ id: 'color-contrast', enabled: false }],
})

const fetchMock = createFetchMock(vi)
fetchMock.enableMocks()
fetchMock.mockResponse((req) => {
  console.error(String.raw`
  ----------------------------------------------------------------------------
  /!\ UNMOCKED FETCH CALL TO :  [${req.method}] ${req.url}
  ----------------------------------------------------------------------------
  `)

  // We do not await this Promise so that Vitest considers it as
  // an unhandled rejection and thus fails the test
  // (otherwise the console.error will appear but not fail the test)
  void Promise.reject(new Error('Unmocked fetch call'))

  // And now return a Promise so that fetchMock is happy
  return Promise.reject(new Error('Unmocked fetch call'))
})

// Mock the ResizeObserver for Charts
class ResizeObserver {
  observe() {
    // Mock implementation
  }

  unobserve() {
    // Mock implementation
  }

  disconnect() {
    // Mock implementation
  }
}

globalThis.ResizeObserver = ResizeObserver

const IntersectionObserverMock = vi.fn(
  class {
    disconnect = vi.fn()
    observe = vi.fn()
    takeRecords = vi.fn()
    unobserve = vi.fn()
  }
)

vi.stubGlobal('IntersectionObserver', IntersectionObserverMock)

// Fail on console errors and warnings
// https://github.com/thomasbrodusch/vitest-fail-on-console#readme
failOnConsole()

// @radix-ui/react-dismissable-layer >= 1.1.12 sets document.body.style.pointerEvents = "none"
// when a layer opens with disableOutsidePointerEvents. If a test unmounts the component while
// the dropdown is still open, the cleanup effect may not restore the body style, causing
// @testing-library/user-event v14 to throw
beforeEach(() => {
  document.body.style.pointerEvents = ''
})

// jsdom logs `Not implemented: navigation to another Document` whenever a test triggers a real navigation.
// These are inherent jsdom limitations (https://github.com/jsdom/jsdom/issues/2112), not actionable test issues,
// so we strip them at the virtualConsole level rather than hiding `console.error` downstream.
const { virtualConsole } = (globalThis as unknown as { jsdom: JSDOM }).jsdom
const previousListeners = virtualConsole.listeners('jsdomError')
virtualConsole.removeAllListeners('jsdomError')
virtualConsole.on('jsdomError', (error) => {
  if (
    error.message?.startsWith('Not implemented: navigation to another Document')
  ) {
    return
  }

  for (const listener of previousListeners) {
    listener(error)
  }
})
