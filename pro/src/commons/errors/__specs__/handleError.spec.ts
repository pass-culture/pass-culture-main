import { clearList } from 'commons/store/snackBar/reducer'
import { listSelector } from 'commons/store/snackBar/selectors'
import { rootStore } from 'commons/store/store'

import { SnackBarVariant } from '@/design-system/SnackBar/SnackBar'

import { handleError } from '../handleError'
import type { FrontendErrorOptions } from '../types'

const mockedSentry = vi.hoisted(() => {
  const setContextMock = vi.fn()
  const captureException = vi.fn()
  const withScopeMock = vi.fn(
    (cb: (scope: { setContext: (e: unknown) => void }) => void) =>
      cb({ setContext: setContextMock })
  )

  return { setContextMock, captureException, withScopeMock }
})
vi.mock('@sentry/browser', () => ({
  withScope: mockedSentry.withScopeMock,
  captureException: mockedSentry.captureException,
}))

describe('handleError', () => {
  const error = new Error('Something went wrong')
  const userMessage = 'Oops, an error occurred.'

  afterEach(() => {
    rootStore.dispatch(clearList())
  })

  it('dispatches a notification, logs to Sentry & console', () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())

    handleError(error, userMessage)

    const snackBars = listSelector(rootStore.getState())
    expect(snackBars).toHaveLength(1)
    expect(snackBars[0]).toMatchObject({
      description: userMessage,
      variant: SnackBarVariant.ERROR,
    })

    expect(mockedSentry.captureException).toHaveBeenCalledWith(error)
    expect(mockedSentry.setContextMock).toHaveBeenCalledExactlyOnceWith(
      'default',
      { isUserImpersonated: null }
    )
    expect(consoleErrorSpy).toHaveBeenCalledWith(error)
  })

  it('forwards context to Sentry scope when provided', () => {
    vi.spyOn(console, 'error').mockImplementation(vi.fn())

    const options: FrontendErrorOptions = {
      context: { foo: 'bar', count: 3 },
      userMessage: userMessage, // ignored by handleError signature (we omit in call)
      isSilent: false,
    }

    handleError(error, userMessage, options)

    expect(mockedSentry.setContextMock).toHaveBeenCalledTimes(2)
    expect(mockedSentry.setContextMock).toHaveBeenNthCalledWith(1, 'default', {
      isUserImpersonated: null,
    })
    expect(mockedSentry.setContextMock).toHaveBeenNthCalledWith(
      2,
      'custom',
      options.context
    )
  })

  it('accepts non-Error (unknown) values', () => {
    const consoleErrorSpy = vi
      .spyOn(console, 'error')
      .mockImplementation(vi.fn())

    // passing a string instead of an Error
    handleError('boom', userMessage)

    const snackBars = listSelector(rootStore.getState())
    expect(snackBars).toHaveLength(1)
    expect(snackBars[0]).toMatchObject({
      description: userMessage,
      variant: SnackBarVariant.ERROR,
    })
    expect(mockedSentry.captureException).toHaveBeenCalledWith('boom')
    expect(consoleErrorSpy).toHaveBeenCalledWith('boom')
  })
})
