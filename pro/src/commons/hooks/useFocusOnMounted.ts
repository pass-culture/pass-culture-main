import { useEffect } from 'react'

export const useFocusOnMounted = (selectorOrRef: string | HTMLElement) => {
  useEffect(() => {
    const element =
      typeof selectorOrRef === 'string'
        ? document.querySelector<HTMLElement>(selectorOrRef)
        : selectorOrRef

    element?.focus()
  }, [selectorOrRef])
}
