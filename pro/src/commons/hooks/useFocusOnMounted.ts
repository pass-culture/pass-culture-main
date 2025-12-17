import { useEffect } from 'react'

import { FrontendError } from '../errors/FrontendError'
import { handleUnexpectedError } from '../errors/handleUnexpectedError'

export const useFocusOnMounted = (selectorOrRef: string | HTMLElement) => {
  useEffect(() => {
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
  }, [selectorOrRef])
}
