import { renderHook } from '@testing-library/react'
import type { SWRResponse } from 'swr'

import { useGracefulSwrResponse } from '../useGracefulSwrResponse'
import * as useSnackBarModule from '../useSnackBar'

const useSwrMock = vi.fn<() => SWRResponse>()
vi.mock('swr', () => ({ default: useSwrMock }))

const RELOAD_ERROR_MESSAGE = 'Reload failed'

function makeSwrResponse<Data>(
  overrides: Partial<SWRResponse<Data>> = {}
): SWRResponse<Data> {
  return {
    data: undefined,
    error: undefined,
    isLoading: false,
    isValidating: false,
    mutate: vi.fn() as never,
    ...overrides,
  }
}

function renderUseGracefulSwrResponse<Data>(
  initialSwrResponse: SWRResponse<Data>
) {
  useSwrMock.mockReturnValue(initialSwrResponse)

  return renderHook(() => {
    const swrResponse = useSwrMock()

    return useGracefulSwrResponse<Data>(swrResponse, RELOAD_ERROR_MESSAGE)
  })
}

describe('useGracefulSwrResponse', () => {
  const useSnackBarErrorMock = vi.fn()

  beforeEach(() => {
    vi.spyOn(useSnackBarModule, 'useSnackBar').mockReturnValue({
      error: useSnackBarErrorMock,
      success: vi.fn(),
    })
  })

  describe('on first load', () => {
    it('reports the first-loading state while fetching', () => {
      const { result } = renderUseGracefulSwrResponse(
        makeSwrResponse({ isLoading: true, isValidating: true })
      )

      expect(result.current).toEqual({
        data: undefined,
        hasFirstLoadError: false,
        hasReloadError: false,
        isFirstLoading: true,
        isReloading: false,
      })
    })

    it('reports the loaded data once the request resolves', () => {
      const { result, rerender } = renderUseGracefulSwrResponse<string[]>(
        makeSwrResponse({ isLoading: true, isValidating: true })
      )

      useSwrMock.mockReturnValue(makeSwrResponse({ data: ['offer-1'] }))
      rerender()

      expect(result.current).toEqual({
        data: ['offer-1'],
        hasFirstLoadError: false,
        hasReloadError: false,
        isFirstLoading: false,
        isReloading: false,
      })
    })

    it('reports the first-load error and does NOT trigger a snackbar', () => {
      const { result, rerender } = renderUseGracefulSwrResponse(
        makeSwrResponse({ isLoading: true, isValidating: true })
      )

      useSwrMock.mockReturnValue(makeSwrResponse({ error: new Error('boom') }))
      rerender()

      expect(result.current).toEqual({
        data: undefined,
        hasFirstLoadError: true,
        hasReloadError: false,
        isFirstLoading: false,
        isReloading: false,
      })
      expect(useSnackBarErrorMock).not.toHaveBeenCalled()
    })
  })

  describe('on background revalidation', () => {
    it('reports the reloading state while keeping the previously loaded data', () => {
      const { result, rerender } = renderUseGracefulSwrResponse<string[]>(
        makeSwrResponse({ data: ['offer-1'] })
      )

      useSwrMock.mockReturnValue(
        makeSwrResponse({ data: ['offer-1'], isValidating: true })
      )
      rerender()

      expect(result.current).toEqual({
        data: ['offer-1'],
        hasFirstLoadError: false,
        hasReloadError: false,
        isFirstLoading: false,
        isReloading: true,
      })
    })

    it('exposes the refreshed data once the reload succeeds', () => {
      const { result, rerender } = renderUseGracefulSwrResponse<string[]>(
        makeSwrResponse({ data: ['offer-1'] })
      )

      useSwrMock.mockReturnValue(
        makeSwrResponse({ data: ['offer-1'], isValidating: true })
      )
      rerender()
      useSwrMock.mockReturnValue(
        makeSwrResponse({ data: ['offer-1', 'offer-2'] })
      )
      rerender()

      expect(result.current).toEqual({
        data: ['offer-1', 'offer-2'],
        hasFirstLoadError: false,
        hasReloadError: false,
        isFirstLoading: false,
        isReloading: false,
      })
    })
  })

  describe('on reload error', () => {
    it('falls back to the previously loaded data and triggers an error snackbar', () => {
      const { result, rerender } = renderUseGracefulSwrResponse<string[]>(
        makeSwrResponse({ data: ['offer-1'] })
      )

      useSwrMock.mockReturnValue(
        makeSwrResponse({ data: ['offer-1'], error: new Error('boom') })
      )
      rerender()

      expect(result.current).toEqual({
        data: ['offer-1'],
        hasFirstLoadError: false,
        hasReloadError: true,
        isFirstLoading: false,
        isReloading: false,
      })
      expect(useSnackBarErrorMock).toHaveBeenCalledExactlyOnceWith(
        RELOAD_ERROR_MESSAGE
      )
    })

    it('recovers cleanly once the next reload succeeds', () => {
      const { result, rerender } = renderUseGracefulSwrResponse<string[]>(
        makeSwrResponse({ data: ['offer-1'] })
      )

      useSwrMock.mockReturnValue(
        makeSwrResponse({ data: ['offer-1'], error: new Error('boom') })
      )
      rerender()
      useSwrMock.mockReturnValue(
        makeSwrResponse({ data: ['offer-1', 'offer-2'] })
      )
      rerender()

      expect(result.current).toEqual({
        data: ['offer-1', 'offer-2'],
        hasFirstLoadError: false,
        hasReloadError: false,
        isFirstLoading: false,
        isReloading: false,
      })
    })
  })
})
