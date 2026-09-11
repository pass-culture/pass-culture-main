import { useEffect, useRef } from 'react'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'
import { listSelector } from '@/commons/store/snackBar/selectors'

export const usePageTitle = () => {
  const currentRoute = useCurrentRoute()
  const snackBars = useAppSelector(listSelector)
  const hasActiveSnackBar = snackBars.length > 0
  // Read through a ref so a snackbar appearing on its own doesn't re-trigger the navigation effect.
  const hasActiveSnackBarRef = useRef(false)
  hasActiveSnackBarRef.current = hasActiveSnackBar

  const announceTitle = (title?: string) => {
    const pageTitleAnnouncer = document.getElementById('page-title-announcer')
    if (pageTitleAnnouncer && title) {
      pageTitleAnnouncer.textContent = title
    }
  }

  // biome-ignore lint/correctness/useExhaustiveDependencies: we need the effect to re-run on every navigation (even though hasActiveSnackBar isn't read inside the effect body)
  useEffect(() => {
    const title = currentRoute.handle?.title

    const metaTitle = [title ? `${title} - ` : '', 'pass Culture Pro'].join('')

    document.title = metaTitle

    // Skip the assertive announcement when a snackbar is active: it would compete
    // with (and usually cut off) the snackbar's own announcement.
    if (!hasActiveSnackBarRef.current) {
      announceTitle(title)
    }
  }, [currentRoute.handle?.title])

  // Once the snackbar disappears, announce the page title that was held back.
  useEffect(() => {
    if (!hasActiveSnackBar) {
      announceTitle(currentRoute.handle?.title)
    }
  }, [hasActiveSnackBar])
}
