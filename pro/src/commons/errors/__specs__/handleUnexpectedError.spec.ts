import { clearList } from 'commons/store/snackBar/reducer'
import { listSelector } from 'commons/store/snackBar/selectors'
import { rootStore } from 'commons/store/store'

import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import { FrontendError } from '../FrontendError'
import { handleUnexpectedError } from '../handleUnexpectedError'
import type { FrontendErrorOptions } from '../types'

describe('handleUnexpectedError', () => {
  const mockedSentry = vi.hoisted(() => {
    const setContextMock = vi.fn()
    const setExtrasMock = vi.fn()
    const captureException = vi.fn()
    const withScopeMock = vi.fn((cb) =>
      cb({ setContext: setContextMock, setExtras: setExtrasMock })
    )

    return { setContextMock, setExtrasMock, captureException, withScopeMock }
  })
  vi.mock('@sentry/browser', () => ({
    withScope: mockedSentry.withScopeMock,
    captureException: mockedSentry.captureException,
  }))

  const error = new FrontendError('An internal error message.')

  afterEach(() => {
    rootStore.dispatch(clearList())
    vi.clearAllMocks()
  })

  it('dispatches a notification, logs to Sentry & console when not silent', () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())

    const err = new FrontendError('Boom!')

    handleUnexpectedError(err)

    const snackBars = listSelector(rootStore.getState())
    expect(snackBars).toHaveLength(1)
    expect(snackBars[0]).toMatchObject({
      text: 'Une erreur est survenue de notre côté. Veuillez réessayer plus tard.',
      variant: SnackBarVariant.ERROR,
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

    const snackBars = listSelector(rootStore.getState())
    expect(snackBars).toHaveLength(0)

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

  it('forwards context to Sentry scope when provided', () => {
    vi.spyOn(console, 'error').mockImplementation(vi.fn())

    const options: FrontendErrorOptions = {
      context: {
        location: '/test-route',
        userId: 123,
      },
      isSilent: true,
    }

    handleUnexpectedError(error, options)

    expect(mockedSentry.setContextMock).toHaveBeenCalledWith(
      'context',
      options.context
    )
  })

  it('honours a custom userMessage', () => {
    vi.spyOn(console, 'error').mockImplementation(vi.fn())

    const options: FrontendErrorOptions = {
      userMessage: 'Houston, we have a problem…',
    }

    handleUnexpectedError(error, options)

    const snackBars = listSelector(rootStore.getState())
    expect(snackBars).toHaveLength(1)
    expect(snackBars[0]).toMatchObject({
      text: options.userMessage,
      variant: SnackBarVariant.ERROR,
    })
  })
})
