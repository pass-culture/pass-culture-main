import { ApiError } from 'apiClient/v1'
import { ApiRequestOptions } from 'apiClient/v1/core/ApiRequestOptions'
import { ApiResult } from 'apiClient/v1/core/ApiResult'

import {
  getErrorCode,
  getHumanReadableApiError,
  serializeApiErrors,
} from '../helpers'

describe('test apiClient:helpers', () => {
  describe('test getErrorCode', () => {
    it("should return ApiError body's error code", () => {
      const request: ApiRequestOptions = {
        method: 'GET',
        url: 'https://test.url',
      }
      const response: ApiResult = {
        url: 'https://test.url',
        ok: false,
        status: 501,
        statusText: 'UNAUTHORIZED',
        body: {
          error: "Vous n'etes pas autorisé à voir cette page.",
          code: 'UNAUTHORIZED_ACCESS',
        },
      }
      const error = new ApiError(
        request,
        response,
        "Vous n'etes pas autorisé à voir cette page."
      )

      const errorCode = getErrorCode(error)
      expect(errorCode).toBe('UNAUTHORIZED_ACCESS')
    })
  })

  it('should map api response errors to form one without changes', () => {
    const initialError: Record<string, string> = {
      f1: 'e1',
      f2: 'e2',
      f3: 'e3',
    }
    const serializedError = serializeApiErrors(initialError)

    expect(serializedError).toEqual({
      f1: 'e1',
      f2: 'e2',
      f3: 'e3',
    })
  })

  it('should map api response errors to form one with changes', () => {
    const initialError: Record<string, string> = {
      f1: 'e1',
      f2: 'e2',
      f3: 'e3',
    }

    const apiFieldsMap: Record<string, string> = {
      f1: 'f4',
    }
    const serializedError = serializeApiErrors(initialError, apiFieldsMap)

    expect(serializedError).toEqual({
      f4: 'e1',
      f2: 'e2',
      f3: 'e3',
    })
  })
})

const apiErrorFactory = (customBody: any = {}): ApiError => {
  const request: ApiRequestOptions = {
    method: 'GET',
    url: 'https://test.url',
  }
  const response: ApiResult = {
    url: 'https://test.url',
    ok: false,
    status: 500,
    statusText: 'UNAUTHORIZED',
    body: customBody,
  }
  return new ApiError(
    request,
    response,
    "Vous n'etes pas autorisé à voir cette page."
  )
}

describe('getHumanReadableApiError', () => {
  it('should parse a list body', () => {
    expect(
      getHumanReadableApiError(apiErrorFactory([{ global: 'toto' }]))
    ).toBe('toto')
    expect(
      getHumanReadableApiError(
        apiErrorFactory([{ global: 'toto' }, { booking: 'titi' }])
      )
    ).toBe('toto titi')
  })

  it('should parse a dict body', () => {
    expect(getHumanReadableApiError(apiErrorFactory({ global: 'toto' }))).toBe(
      'toto'
    )
    expect(
      getHumanReadableApiError(apiErrorFactory({ global: ['toto'] }))
    ).toBe('toto')
    expect(
      getHumanReadableApiError(
        apiErrorFactory({
          booking: ['tata'],
          global: ['toto', 'titi'],
        })
      )
    ).toBe('tata toto titi')
  })

  it('parse empty error', () => {
    expect(getHumanReadableApiError(apiErrorFactory([]))).toBe(
      'Une erreur s’est produite, veuillez réessayer'
    )
    expect(getHumanReadableApiError(apiErrorFactory({}))).toBe(
      'Une erreur s’est produite, veuillez réessayer'
    )
    expect(getHumanReadableApiError(apiErrorFactory(''))).toBe(
      'Une erreur s’est produite, veuillez réessayer'
    )
    expect(getHumanReadableApiError(apiErrorFactory(null))).toBe(
      'Une erreur s’est produite, veuillez réessayer'
    )
  })
})
