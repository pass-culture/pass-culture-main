import { useEffect } from 'react'

import { FrontendError } from '../errors/FrontendError'
import { handleUnexpectedError } from '../errors/handleUnexpectedError'

export const useFocusOnMounted = (
  selectorOrRef: string | HTMLElement,
  isLoading = false
) => {
  useEffect(() => {
    if (isLoading) {
      return
    }

    const element =
      typeof selectorOrRef === 'string'
        ? document.querySelector<HTMLElement>(selectorOrRef)
        : selectorOrRef
    if (!element) {
      handleUnexpectedError(
        new FrontendError('`element` is null, there is nothing to focus.')
      )

      return
    }

    element.focus()
  }, [isLoading, selectorOrRef])
}
