import { useEffect } from 'react'

import { useCurrentRoute } from '@/commons/hooks/useCurrentRoute'

export const usePageTitle = () => {
  const currentRoute = useCurrentRoute()

  useEffect(() => {
    const title = currentRoute.handle?.title

    const metaTitle = [title ? `${title} - ` : '', 'pass Culture Pro'].join('')

    document.title = metaTitle

    const pageTitleAnnouncer = document.getElementById('page-title-announcer')
    if (pageTitleAnnouncer && title) {
      pageTitleAnnouncer.textContent = title
    }
  }, [currentRoute.handle?.title])
}
