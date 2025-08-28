import { closeNotification } from 'commons/store/notifications/reducer'
import { rootStore } from 'commons/store/store'

import { handleError } from '../handleError'
import type { FrontendErrorOptions } from '../types'

describe('handleError', () => {
  const mockedSentry = vi.hoisted(() => {
    const setExtrasMock = vi.fn()
    const captureException = vi.fn()
    const withScopeMock = vi.fn(
      (cb: (scope: { setExtras: (e: unknown) => void }) => void) =>
        cb({ setExtras: setExtrasMock })
    )

    return { setExtrasMock, captureException, withScopeMock }
  })
  vi.mock('@sentry/browser', () => ({
    withScope: mockedSentry.withScopeMock,
    captureException: mockedSentry.captureException,
  }))

  const error = new Error('Something went wrong')
  const userMessage = 'Oops, an error occurred.'

  afterEach(() => {
    rootStore.dispatch(closeNotification())
    vi.clearAllMocks()
  })

  it('dispatches a notification, logs to Sentry & console', () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())

    handleError(error, userMessage)

    const state = rootStore.getState()
    expect(state.notification.notification).toStrictEqual({
      text: userMessage,
      type: 'error',
      duration: expect.any(Number),
    })

    expect(mockedSentry.captureException).toHaveBeenCalledWith(error)
    expect(mockedSentry.setExtrasMock).not.toHaveBeenCalled()
    expect(consoleErrorSpy).toHaveBeenCalledWith(error)
  })

  it('forwards extras to Sentry scope when provided', () => {
    vi.spyOn(console, 'error').mockImplementation(vi.fn())

    const options: FrontendErrorOptions = {
      extras: { foo: 'bar', count: 3 },
      userMessage: userMessage, // ignored by handleError signature (we omit in call)
      isSilent: false,
    }

    handleError(error, userMessage, options)

    expect(mockedSentry.setExtrasMock).toHaveBeenCalledWith(options.extras)
  })

  it('accepts non-Error (unknown) values', () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())

    // passing a string instead of an Error
    handleError('boom', userMessage)

    const state = rootStore.getState()
    expect(state.notification.notification?.text).toBe(userMessage)
    expect(mockedSentry.captureException).toHaveBeenCalledWith('boom')
    expect(consoleErrorSpy).toHaveBeenCalledWith('boom')
  })
})
