import { useEffect } from 'react'
import { useLocation } from 'react-router'

export const useFocus = (): void => {
  const { pathname } = useLocation()

  // biome-ignore lint/correctness/useExhaustiveDependencies: we need the effect to re-run on every navigation (even though pathname isn't read inside the effect body) so that the focus is always on the top of the page
  useEffect(() => {
    const topPageLink = document.getElementById('top-page')

    if (topPageLink) {
      topPageLink.focus()
    }
  }, [pathname])
}
