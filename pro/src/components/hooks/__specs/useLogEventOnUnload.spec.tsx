import { cleanup, renderHook } from '@testing-library/react-hooks'

import useLogEventOnUnload from '../useLogEventOnUnload'

describe('useBeforeUnload', () => {
  describe('When the hook is initialised', () => {
    test('It should register the correct event listener and unregister on unmount', async () => {
      const spyAddEvent = jest.fn()
      const spyRemoveEvent = jest.fn()
      const mockLogEvent = jest.fn()
      jest.spyOn(window, 'addEventListener').mockImplementation(spyAddEvent)
      jest
        .spyOn(window, 'removeEventListener')
        .mockImplementation(spyRemoveEvent)
      expect(
        spyAddEvent.mock.calls
          .map(args => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(0)
      expect(
        spyRemoveEvent.mock.calls
          .map(args => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(0)
      await renderHook(() => useLogEventOnUnload(mockLogEvent))
      expect(
        spyAddEvent.mock.calls
          .map(args => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(1)
      expect(
        spyRemoveEvent.mock.calls
          .map(args => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(0)
      cleanup()
      expect(
        spyRemoveEvent.mock.calls
          .map(args => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(1)
      expect(
        spyAddEvent.mock.calls
          .map(args => args[0] === 'beforeunload')
          .filter(Boolean).length
      ).toEqual(1)
    })
  })
})
