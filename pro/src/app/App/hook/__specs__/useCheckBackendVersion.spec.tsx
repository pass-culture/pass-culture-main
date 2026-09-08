import { act, renderHook } from '@testing-library/react'

import { BACKEND_VERSION_MISMATCH_EVENT } from '@/apiClient/api'

import { useCheckBackendVersion } from '../useCheckBackendVersion'

describe('useCheckBackendVersion', () => {
  it('should not report a mismatch before the event is emitted', () => {
    const { result } = renderHook(() => useCheckBackendVersion())

    expect(result.current).toBe(false)
  })

  it('should report a mismatch when the API interceptor emits the event', () => {
    const { result } = renderHook(() => useCheckBackendVersion())

    act(() => {
      window.dispatchEvent(new Event(BACKEND_VERSION_MISMATCH_EVENT))
    })

    expect(result.current).toBe(true)
  })

  it('should stop listening when unmounted', () => {
    const { result, unmount } = renderHook(() => useCheckBackendVersion())

    unmount()
    window.dispatchEvent(new Event(BACKEND_VERSION_MISMATCH_EVENT))

    expect(result.current).toBe(false)
  })
})
