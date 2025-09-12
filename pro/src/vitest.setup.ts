import 'regenerator-runtime/runtime'
import { expect } from 'vitest'
import '@testing-library/jest-dom/vitest'
import { HttpResponse, http } from 'msw'
import { setupServer } from 'msw/node'
import * as matchers from 'vitest-axe/matchers'
import failOnConsole from 'vitest-fail-on-console'
import 'vitest-canvas-mock'

expect.extend(matchers)

const httpHandlerMock = () => HttpResponse.json({})
export const fetchMockServer = setupServer(
  http.get('*', httpHandlerMock),
  http.post('*', httpHandlerMock),
  http.put('*', httpHandlerMock),
  http.patch('*', httpHandlerMock),
  http.delete('*', httpHandlerMock),
  http.options('*', httpHandlerMock),
  http.head('*', httpHandlerMock)
)
beforeAll(() => void fetchMockServer.listen({ onUnhandledRequest: 'error' }))
afterEach(() => void fetchMockServer.resetHandlers())
afterAll(() => void fetchMockServer.close())

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
