import { closeNotification } from 'commons/store/notifications/reducer'
import { rootStore } from 'commons/store/store'

import { FrontendError } from '../FrontendError'
import { handleUnexpectedError } from '../handleUnexpectedError'
import type { FrontendErrorOptions } from '../types'

describe('handleUnexpectedError', () => {
  const mockedSentry = vi.hoisted(() => {
    const setExtrasMock = vi.fn()
    const captureException = vi.fn()
    const withScopeMock = vi.fn((cb) => cb({ setExtras: setExtrasMock }))

    return { setExtrasMock, captureException, withScopeMock }
  })
  vi.mock('@sentry/browser', () => ({
    withScope: mockedSentry.withScopeMock,
    captureException: mockedSentry.captureException,
  }))

  const error = new FrontendError('An internal error message.')

  afterEach(() => {
    rootStore.dispatch(closeNotification())
    vi.clearAllMocks()
  })

  it('dispatches a notification, logs to Sentry & console when not silent', () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())

    const err = new FrontendError('Boom!')

    handleUnexpectedError(err)

    const state = rootStore.getState()
    expect(state.notification.notification).toStrictEqual({
      text: 'Une erreur est survenue de notre côté. Veuillez réessayer plus tard.',
      type: 'error',
      duration: expect.any(Number),
    })

    expect(mockedSentry.captureException).toHaveBeenCalledWith(err)
    expect(mockedSentry.setExtrasMock).not.toHaveBeenCalled()

    expect(consoleErrorSpy).toHaveBeenCalledWith(err)
  })

  it('does NOT dispatch a notification when isSilent is true', () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())

    const options: FrontendErrorOptions = {
      isSilent: true,
    }

    handleUnexpectedError(error, options)

    const state = rootStore.getState()
    expect(state.notification.notification).toBeNull()

    expect(mockedSentry.captureException).toHaveBeenCalledOnce()

    expect(consoleErrorSpy).toHaveBeenCalledWith(error)
  })

  it('forwards extras to Sentry scope when provided', () => {
    vi.spyOn(console, 'error').mockImplementation(vi.fn())

    const options: FrontendErrorOptions = {
      extras: {
        foo: 'bar',
        id: 7,
      },
    }

    handleUnexpectedError(error, options)

    expect(mockedSentry.setExtrasMock).toHaveBeenCalledWith(options.extras)
  })

  it('honours a custom userMessage', () => {
    vi.spyOn(console, 'error').mockImplementation(vi.fn())

    const options: FrontendErrorOptions = {
      userMessage: 'Houston, we have a problem…',
    }

    handleUnexpectedError(error, options)

    const state = rootStore.getState()
    expect(state.notification.notification).toStrictEqual({
      text: options.userMessage,
      type: 'error',
      duration: expect.any(Number),
    })
  })
})
