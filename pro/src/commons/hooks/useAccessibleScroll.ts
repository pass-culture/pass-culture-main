import { useRef } from 'react'

import { assertOrFrontendError } from '../errors/assertOrFrontendError'
import { useMediaQuery } from './useMediaQuery'

/**
 * Custom hook to help with smooth scrolling and live region accessibility messages.
 * Works with the `AccessibleScrollContainer` component.
 *
 * @param {string} [initialLiveMessage] - The initial ARIA live region message.
 * @param {string} [options.selector] - (Optional) The selector of the scrollable container.
 *
 * @returns {{
 *   contentWrapperRef: React.RefObject<HTMLDivElement>,
 *   scrollToContentWrapper: () => void
 * }}
 * - `contentWrapperRef`: Ref to the scrollable container used for focus and positioning. Must be provided to the `AccessibleScrollContainer` component.
 * - `scrollToContentWrapper`: Function to smoothly scroll and focus the container on page change.
 */

type Options = {
  selector?: string
}

export const useAccessibleScroll = ({ selector }: Options = {}) => {
  const contentWrapperRef = useRef<HTMLDivElement>(null)

  const userPrefersReducedMotion = useMediaQuery(
    '(prefers-reduced-motion: reduce)'
  )

  const scrollToContentWrapper = () => {
    if (contentWrapperRef.current) {
      const wrapperRect = contentWrapperRef.current.getBoundingClientRect()
      let target: Window | Element | null = globalThis.window
      let offset: number = wrapperRect.top + globalThis.window.scrollY

      // If a selector is provided, scroll to the container with the given selector
      if (selector) {
        const pageWrapper = document.querySelector(selector)

        assertOrFrontendError(
          pageWrapper !== null,
          `[useAccessibleScroll] Cannot scroll to ${selector} because it is not present in the DOM`,
          { isSilent: true }
        )

        const pageRect = pageWrapper.getBoundingClientRect()
        offset = wrapperRect.top - pageRect.top + pageWrapper.scrollTop

        target = pageWrapper
      }

      // Focus before scrolling in order to not break the smooth animation (if applicable)
      contentWrapperRef.current?.focus()
      target.scrollTo({
        top: offset,
        behavior: userPrefersReducedMotion ? 'instant' : 'smooth',
      })
    }
  }

  return {
    contentWrapperRef,
    scrollToContentWrapper,
  }
}
