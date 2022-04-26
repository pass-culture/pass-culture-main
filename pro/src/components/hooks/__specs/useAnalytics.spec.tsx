import { renderHook } from '@testing-library/react-hooks'

import useAnalytics from '../useAnalytics'

test('should set logEvent', () => {
  const hook = renderHook(() => useAnalytics(undefined))
  hook.rerender()

  expect(hook.result.current.logEvent).toBeDefined()
})

test('should set currentUserId', () => {
  const hook = renderHook(() => useAnalytics('toto'))
  hook.rerender('toto')
  expect(hook.result.current.currentUserId).toBe('toto')
})
