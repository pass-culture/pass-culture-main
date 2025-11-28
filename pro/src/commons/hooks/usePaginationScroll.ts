import { useEffect, useRef, useState } from 'react'

import { useMediaQuery } from './useMediaQuery'

/**
 * Custom hook to help with pagination scroll and live region accessibility messages.
 * Works with the `AccessibleScrollContainer` component.
 *
 * @param {number} page - The current active page number.
 * @param {number} pageCount - The total number of available pages.
 * @param {string} [initialLiveMessage] - (Optional) The initial ARIA live region message, defaults to "Page {page} sur {pageCount}".
 * @param {string} [options.selector] - (Optional) The selector of the scrollable container, defaults to '#content-wrapper'.
 *
 * @returns {{
 *   contentWrapperRef: React.RefObject<HTMLDivElement>,
 *   liveMessage: string,
 *   setLiveMessage: React.Dispatch<React.SetStateAction<string>>,
 *   scrollToContentWrapper: () => void
 * }}
 * - `contentWrapperRef`: Ref to the scrollable container used for focus and positioning. Must be provided to the `AccessibleScrollContainer` component.
 * - `liveMessage`: Current message for assistive technologies to announce.
 * - `setLiveMessage`: Setter to programmatically update the live region message.
 * - `scrollToContentWrapper`: Function to smoothly scroll and focus the container on page change.
 */

type Options = {
  initialLiveMessage?: string
  selector?: string
}

export const usePaginationScroll = (
  page: number,
  pageCount: number,
  {
    initialLiveMessage = `Page ${page} sur ${pageCount}`,
    selector,
  }: Options = {}
) => {
  const contentWrapperRef = useRef<HTMLDivElement>(null)
  const liveMessageInitialized = useRef(false)

  const userPrefersReducedMotion = useMediaQuery(
    '(prefers-reduced-motion: reduce)'
  )

  const [liveMessage, setLiveMessage] = useState('')

  useEffect(() => {
    // Skip the very first render to avoid announcing the initial page state
    // (Screen readers already announce the initial DOM)
    if (!liveMessageInitialized.current) {
      liveMessageInitialized.current = true
      return
    }

    setLiveMessage(initialLiveMessage)
  }, [initialLiveMessage])

  const scrollToContentWrapper = () => {
    if (contentWrapperRef.current) {
      const wrapperRect = contentWrapperRef.current.getBoundingClientRect()
      let target: Element | Window = window
      let offset: number = wrapperRect.top + window.scrollY

      // If a selector is provided, scroll to the container with the given selector
      if (selector) {
        const pageWrapper = document.querySelector(selector)
        if (pageWrapper !== null) {
          const pageRect = pageWrapper.getBoundingClientRect()
          offset = wrapperRect.top - pageRect.top + pageWrapper.scrollTop

          target = pageWrapper
        }
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
    liveMessage,
    setLiveMessage,
    scrollToContentWrapper,
  }
}
