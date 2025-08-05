import { useCallback, useRef } from 'react'

export function useFunctionOnce(callback: (() => void) | undefined) {
  const hasRenderedOnce = useRef<boolean>(false)

  return useCallback(() => {
    if (!hasRenderedOnce.current) {
      hasRenderedOnce.current = true
      if (callback) {
        callback()
      }
    }
  }, [callback])
}
