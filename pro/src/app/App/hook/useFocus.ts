import { useEffect, useRef } from 'react'
import { useLocation } from 'react-router'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { listSelector } from '@/commons/store/snackBar/selectors'

export const useFocus = (): void => {
  const { pathname } = useLocation()
  const snackBars = useAppSelector(listSelector)
  // Read through a ref so a snackbar appearing/disappearing on its own doesn't re-trigger this effect.
  const hasActiveSnackBarRef = useRef(false)
  hasActiveSnackBarRef.current = snackBars.length > 0

  // biome-ignore lint/correctness/useExhaustiveDependencies: we need the effect to re-run on every navigation (even though pathname isn't read inside the effect body) so that the focus is always on the top of the page
  useEffect(() => {
    // Skip stealing focus when a snackbar is active: it would fire right after the snackbar's
    // own focus/announcement and prevent screen reader users from ever hearing the message.
    if (!hasActiveSnackBarRef.current) {
      const topPageLink = document.getElementById('top-page')

      if (topPageLink) {
        topPageLink.focus()
      }
    }

    // As "topPageLink" is a non-interactive <div tabIndex={-1}>, focusing above is not sufficient to guarantee that the browser scrolls to the top
    // So we must force the #content-wrapper container to go to top
    document.getElementById('content-wrapper')?.scrollTo(0, 0)
  }, [pathname])
}
