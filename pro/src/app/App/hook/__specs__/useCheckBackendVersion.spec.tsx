import { act, renderHook } from '@testing-library/react'

import {
  BACKEND_VERSION_HIGHER_EVENT,
  BACKEND_VERSION_LOWER_EVENT,
} from '@/apiClient/api'

import { useCheckBackendVersion } from '../useCheckBackendVersion'

describe('useCheckBackendVersion', () => {
  it('should not report a mismatch before the event is emitted', () => {
    const { result } = renderHook(() => useCheckBackendVersion())

    expect(result.current).toBe('equal')
  })

  it.each([
    [BACKEND_VERSION_HIGHER_EVENT, 'higher'],
    [BACKEND_VERSION_LOWER_EVENT, 'lower'],
  ] as const)(
    'should report a mismatch when the API interceptor emits %s',
    (eventName, expectedComparison) => {
      const { result } = renderHook(() => useCheckBackendVersion())

      act(() => {
        window.dispatchEvent(new Event(eventName))
      })

      expect(result.current).toBe(expectedComparison)
    }
  )

  it('should stop listening when unmounted', () => {
    const { result, unmount } = renderHook(() => useCheckBackendVersion())

    unmount()
    window.dispatchEvent(new Event(BACKEND_VERSION_HIGHER_EVENT))
    window.dispatchEvent(new Event(BACKEND_VERSION_LOWER_EVENT))

    expect(result.current).toBe('equal')
  })
})
