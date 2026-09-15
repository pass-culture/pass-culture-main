import { useEffect, useRef } from 'react'
import { useLocation, useNavigate } from 'react-router'

import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useSnackBar } from '@/commons/hooks/useSnackBar'
import { listSelector } from '@/commons/store/snackBar/selectors'
import { SNACKBAR_ITEM_SELECTOR } from '@/design-system/SnackBar/SnackBar'

export const useFocus = (): void => {
  const location = useLocation()
  const { pathname } = location
  const navigate = useNavigate()
  const snackBar = useSnackBar()
  const snackBars = useAppSelector(listSelector)
  // Read through a ref so a snackbar appearing/disappearing on its own doesn't re-trigger this effect.
  const hasActiveSnackBarRef = useRef(false)
  hasActiveSnackBarRef.current = snackBars.length > 0

  // biome-ignore lint/correctness/useExhaustiveDependencies: we need the effect to re-run on every navigation (even though pathname isn't read inside the effect body) so that the focus is always on the top of the page
  useEffect(() => {
    // A page can carry a success message through navigation `state` (e.g. a
    // "save and quit" action): shown here, once the destination page has
    // taken over, instead of racing with the navigation that triggered it.
    const successMessage = (
      location.state as { successMessage?: string } | null
    )?.successMessage

    let rafId: number | undefined

    if (successMessage) {
      snackBar.success(successMessage)
      hasActiveSnackBarRef.current = true
      navigate(location.pathname + location.search, {
        replace: true,
        state: null,
      })

      // Deferred to the next frame: the dispatch above hasn't re-rendered the
      // snack bar into the DOM yet, so querying for it now would find nothing.
      rafId = requestAnimationFrame(() => {
        document.querySelector<HTMLElement>(SNACKBAR_ITEM_SELECTOR)?.focus()
      })
    } else if (hasActiveSnackBarRef.current) {
      // Read the activeSnackBar on navigation (ex : when leaving a screen with "save and quit" option)
      const activeSnackBar = document.querySelector<HTMLElement>(
        SNACKBAR_ITEM_SELECTOR
      )
      if (activeSnackBar) {
        activeSnackBar.blur()
        rafId = requestAnimationFrame(() => {
          activeSnackBar.focus()
        })
      }
    } else {
      document.getElementById('top-page')?.focus()
    }

    // As "topPageLink" is a non-interactive <div tabIndex={-1}>, focusing above is not sufficient to guarantee that the browser scrolls to the top
    // So we must force the #content-wrapper container to go to top
    document.getElementById('content-wrapper')?.scrollTo(0, 0)

    return () => {
      if (rafId !== undefined) {
        cancelAnimationFrame(rafId)
      }
    }
  }, [pathname])
}
