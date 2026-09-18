import cn from 'classnames'
import { useEffect, useRef, useState } from 'react'
import { createPortal } from 'react-dom'

import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { removeSnackBar } from '@/commons/store/snackBar/reducer'
import {
  isStickyBarOpenSelector,
  listSelector,
} from '@/commons/store/snackBar/selectors'
import {
  SnackBar,
  type SnackBarVariant,
  VARIANT_CONFIG,
} from '@/design-system/SnackBar/SnackBar'

import styles from './SnackBarContainer.module.scss'

/**
 * The SnackBarContainer component is used to display snackbars of different types.
 * It supports displaying snackbars such as errors and success
 *
 * ---
 * **Important: Use `list` selector to get the snackbars to be displayed.**
 * ---
 *
 * @returns {JSX.Element} The rendered SnackBarContainer component.
 */
export const SnackBarContainer = (): JSX.Element => {
  const snackBars = useAppSelector(listSelector)
  const dispatch = useAppDispatch()
  const isStickyBarOpen = useAppSelector(isStickyBarOpenSelector)
  const [portalTarget, setPortalTarget] = useState<Element>(() => document.body)
  const [announcement, setAnnouncement] = useState('')
  const previousSnackBarIdsRef = useRef<Set<string>>(new Set())

  useEffect(() => {
    setPortalTarget(
      document.querySelector('dialog[data-snackbar-portal][open]') ??
        document.body
    )
  }, [snackBars.length])

  useEffect(() => {
    const newSnackBars = snackBars.filter(
      (snackBar) => !previousSnackBarIdsRef.current.has(snackBar.id)
    )
    previousSnackBarIdsRef.current = new Set(
      snackBars.map((snackBar) => snackBar.id)
    )

    if (newSnackBars.length === 0) {
      return
    }

    setAnnouncement('')
    const timeoutId = setTimeout(() => {
      setAnnouncement(
        newSnackBars
          .map((snackBar) =>
            getSnackBarAnnouncement(snackBar.variant, snackBar.description)
          )
          .join('. ')
      )
    }, 100)

    return () => clearTimeout(timeoutId)
  }, [snackBars])

  const sortedSnackBars = snackBars
    .slice()
    .sort(
      (a, b) =>
        new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
    )

  // Single source of truth for the accessible text of a snack bar, so any
  // place that needs to announce it (the snack bar itself, the always-present
  // live region in SnackBarContainer) stays in sync.
  const getSnackBarAnnouncement = (
    variant: SnackBarVariant,
    description: string
  ): string => `${VARIANT_CONFIG[variant].ariaLabel} : ${description}`

  return createPortal(
    <>
      <div className={styles['visually-hidden']}>
        <div role="alert" aria-live="assertive" aria-atomic="true">
          {announcement || '\u00A0'}
        </div>
      </div>
      <aside
        className={cn(
          styles['snack-bar-container'],
          isStickyBarOpen && styles['with-sticky-action-bar']
        )}
      >
        {sortedSnackBars.map((snackBar, index) => (
          <SnackBar
            key={snackBar.id}
            variant={snackBar.variant}
            description={snackBar.description}
            onClose={() => dispatch(removeSnackBar(snackBar.id))}
            testId={`global-snack-bar-${snackBar.variant}-${index}`}
            targetFocusId={snackBar.targetFocusId}
          />
        ))}
      </aside>
    </>,
    portalTarget
  )
}
