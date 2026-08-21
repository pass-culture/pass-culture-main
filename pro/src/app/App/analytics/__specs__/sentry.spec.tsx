import type { BrowserOptions, ErrorEvent, EventHint } from '@sentry/browser'
import * as Sentry from '@sentry/browser'

import { makeApiError } from '@/commons/utils/factories/errorFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'

import { initializeSentry, useSentry } from '../sentry'

vi.mock('@sentry/browser', () => ({
  init: vi.fn(),
  setUser: vi.fn(),
}))

vi.mock('@sentry/react', () => ({
  reactRouterV7BrowserTracingIntegration: vi.fn(),
}))

const SIGNUP_URL =
  'https://pro.example.com/inscription/compte/confirmation/A1B2'
const SCRUBBED_SIGNUP_URL =
  'https://pro.example.com/inscription/compte/confirmation/[TOKEN]'

type TransactionEvent = Awaited<
  ReturnType<NonNullable<BrowserOptions['beforeSendTransaction']>>
>

function getSentryOption<Key extends keyof BrowserOptions>(
  key: Key
): NonNullable<BrowserOptions[Key]> {
  initializeSentry()

  const option = vi.mocked(Sentry.init).mock.calls[0]?.[0]?.[key]
  if (!option) {
    throw new Error(`Sentry.init got no \`${String(key)}\` option.`)
  }

  return option
}

function send(
  event: Omit<ErrorEvent, 'type'> = {},
  hint: EventHint = {}
): ErrorEvent | null {
  const beforeSend = getSentryOption('beforeSend')

  // `type: undefined` is what tells an error event apart from a transaction one
  return beforeSend({ ...event, type: undefined }, hint) as ErrorEvent | null
}

describe('initializeSentry', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe('beforeSend', () => {
    it('should scrub the signup token from the event tags, request and transaction', () => {
      const event = send({
        tags: { url: SIGNUP_URL },
        request: { url: SIGNUP_URL },
        transaction: SIGNUP_URL,
      })

      expect(event?.tags?.['url']).toBe(SCRUBBED_SIGNUP_URL)
      expect(event?.request?.url).toBe(SCRUBBED_SIGNUP_URL)
      expect(event?.transaction).toBe(SCRUBBED_SIGNUP_URL)
    })

    it('should scrub the signup token from the normalized request metadata', () => {
      const event = send({
        sdkProcessingMetadata: { normalizedRequest: { url: SIGNUP_URL } },
      })

      expect(event?.sdkProcessingMetadata?.normalizedRequest?.url).toBe(
        SCRUBBED_SIGNUP_URL
      )
    })

    it.each(['Timeout', 'Timeout (u)'])(
      'should drop the recaptcha and analytics "%s" error',
      (originalException) => {
        expect(send({}, { originalException })).toBeNull()
      }
    )

    it('should attach an API error context when the exception is an ApiError', () => {
      const apiError = makeApiError({
        status: 500,
        url: 'https://api.example.com/offers/123/stocks',
        body: { global: ['Une erreur technique est survenue'] },
      })

      const event = send({}, { originalException: apiError })

      expect(event?.contexts?.['API error']).toStrictEqual({
        endpoint: 'GET /offers/{id}/stocks',
        status: 500,
        url: 'https://api.example.com/offers/123/stocks',
        body: { global: ['Une erreur technique est survenue'] },
      })
    })

    it('should scrub the signup token from the API error context url', () => {
      const apiError = makeApiError({
        status: 400,
        url: 'https://api.example.com/users/validate_signup/A1B2',
      })

      const event = send({}, { originalException: apiError })

      expect(event?.contexts?.['API error']?.['url']).toBe(
        'https://api.example.com/users/validate_signup/[TOKEN]'
      )
    })

    it('should keep the contexts already set on the event', () => {
      const event = send(
        { contexts: { default: { isUserImpersonated: true } } },
        { originalException: makeApiError() }
      )

      expect(event?.contexts?.default).toStrictEqual({
        isUserImpersonated: true,
      })
    })

    it('should not attach an API error context for other errors', () => {
      const event = send({}, { originalException: new Error('Oops') })

      expect(event?.contexts?.['API error']).toBeUndefined()
    })

    it('should not set a fingerprint, so that Sentry groups the event itself', () => {
      const event = send({}, { originalException: makeApiError() })

      expect(event?.fingerprint).toBeUndefined()
    })
  })

  describe('beforeSendTransaction', () => {
    it('should scrub the signup token from the transaction event', () => {
      const beforeSendTransaction = getSentryOption('beforeSendTransaction')

      const transactionEvent = beforeSendTransaction(
        {
          type: 'transaction',
          request: { url: SIGNUP_URL },
          transaction: SIGNUP_URL,
          sdkProcessingMetadata: { normalizedRequest: { url: SIGNUP_URL } },
        },
        {}
      ) as TransactionEvent

      expect(transactionEvent?.request?.url).toBe(SCRUBBED_SIGNUP_URL)
      expect(transactionEvent?.transaction).toBe(SCRUBBED_SIGNUP_URL)
      expect(
        transactionEvent?.sdkProcessingMetadata?.normalizedRequest?.url
      ).toBe(SCRUBBED_SIGNUP_URL)
    })
  })

  describe('beforeBreadcrumb', () => {
    it('should scrub the signup token from the breadcrumb url', () => {
      const beforeBreadcrumb = getSentryOption('beforeBreadcrumb')

      const breadcrumb = beforeBreadcrumb(
        { data: { url: 'https://api.example.com/users/validate_signup/A1B2' } },
        {}
      )

      expect(breadcrumb?.data?.url).toBe(
        'https://api.example.com/users/validate_signup/[TOKEN]'
      )
    })
  })

  describe('beforeSendSpan', () => {
    it('should scrub the signup token from the span description', () => {
      const beforeSendSpan = getSentryOption('beforeSendSpan')

      const span = beforeSendSpan({
        description: 'GET https://api.example.com/users/validate_signup/A1B2',
      } as Parameters<typeof beforeSendSpan>[0])

      expect(span.description).toBe(
        'GET https://api.example.com/users/validate_signup/[TOKEN]'
      )
    })
  })
})

describe('useSentry', () => {
  const TestComponent = (): null => {
    useSentry()

    return null
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('should identify the current user to Sentry', () => {
    renderWithProviders(<TestComponent />, {
      user: sharedCurrentUserFactory({ id: 42 }),
    })

    expect(Sentry.setUser).toHaveBeenCalledWith({ id: '42' })
  })

  it('should not identify anyone when nobody is logged in', () => {
    renderWithProviders(<TestComponent />)

    expect(Sentry.setUser).not.toHaveBeenCalled()
  })
})
