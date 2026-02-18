import { useEffect } from 'react'
import { useLocation } from 'react-router'

import { findCurrentRoute } from '@/app/AppRouter/findCurrentRoute'
import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'

export const usePageTitle = () => {
  const location = useLocation()
  const currentRoute = useCurrentRoute()

  useEffect(() => {
    const legacyCurrentRoute = findCurrentRoute(location)

    const title = currentRoute.handle?.title ?? legacyCurrentRoute?.title

    const metaTitle = [title ? `${title} - ` : '', 'pass Culture Pro'].join('')

    document.title = metaTitle

    const pageTitleAnnouncer = document.getElementById('page-title-announcer')
    if (pageTitleAnnouncer && title) {
      pageTitleAnnouncer.textContent = title
    }
  }, [currentRoute.handle?.title, location])
}
