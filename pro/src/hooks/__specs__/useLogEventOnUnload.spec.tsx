import { cleanup, renderHook } from '@testing-library/react'

import { useLogEventOnUnload } from 'hooks/useLogEventOnUnload'

describe('useBeforeUnload', () => {
  describe('When the hook is initialised', () => {
    test('It should register the correct event listener and unregister on unmount', () => {
      const spyAddEvent = vi.fn()
      const spyRemoveEvent = vi.fn()
      const mockLogEvent = vi.fn()
      vi.spyOn(window, 'addEventListener').mockImplementation(spyAddEvent)
      vi.spyOn(window, 'removeEventListener').mockImplementation(spyRemoveEvent)
      expect(
        spyAddEvent.mock.calls
          .map((args) => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(0)
      expect(
        spyRemoveEvent.mock.calls
          .map((args) => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(0)
      renderHook(() => useLogEventOnUnload(mockLogEvent))
      expect(
        spyAddEvent.mock.calls
          .map((args) => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(1)
      expect(
        spyRemoveEvent.mock.calls
          .map((args) => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(0)
      cleanup()
      expect(
        spyRemoveEvent.mock.calls
          .map((args) => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(1)
      expect(
        spyAddEvent.mock.calls
          .map((args) => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(1)
    })
  })
})
