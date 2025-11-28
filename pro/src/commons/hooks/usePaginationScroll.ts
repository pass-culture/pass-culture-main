import { useCallback, useEffect, useRef, useState } from 'react'

import { useMediaQuery } from './useMediaQuery'

export const usePaginationScroll = (
  page: number,
  pageCount: number,
  liveMessage: string = `Page ${page} sur ${pageCount}`
) => {
  const contentWrapperRef = useRef<HTMLDivElement>(null)
  const tableLiveRegionInitializedRef = useRef(false)

  const userPrefersReducedMotion = useMediaQuery(
    '(prefers-reduced-motion: reduce)'
  )

  const [tableLiveMessage, setTableLiveMessage] = useState('')

  useEffect(() => {
    if (!tableLiveRegionInitializedRef.current) {
      tableLiveRegionInitializedRef.current = true
      return
    }

    setTableLiveMessage(liveMessage)
  }, [liveMessage])

  const scrollToContentWrapper = useCallback(() => {
    const contentWrapper = document.querySelector('#content-wrapper')
    if (contentWrapper instanceof HTMLElement && contentWrapperRef.current) {
      const wrapperRect = contentWrapper.getBoundingClientRect()
      const tableRect = contentWrapperRef.current.getBoundingClientRect()
      const offset = tableRect.top - wrapperRect.top + contentWrapper.scrollTop

      // Focus first
      contentWrapperRef.current?.focus()

      // Then scroll
      contentWrapper.scrollTo({
        top: offset,
        behavior: userPrefersReducedMotion ? 'instant' : 'smooth',
      })
    }
  }, [userPrefersReducedMotion])

  return {
    contentWrapperRef,
    tableLiveMessage,
    setTableLiveMessage,
    scrollToContentWrapper,
  }
}
