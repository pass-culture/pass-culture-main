import cn from 'classnames'
import { useEffect, useState } from 'react'
import { createPortal } from 'react-dom'

import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { removeSnackBar } from '@/commons/store/snackBar/reducer'
import {
  isStickyBarOpenSelector,
  listSelector,
} from '@/commons/store/snackBar/selectors'
import {
  getSnackBarAnnouncement,
  SnackBar,
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

  useEffect(() => {
    setPortalTarget(
      document.querySelector('dialog[data-snackbar-portal][open]') ??
        document.body
    )
  }, [snackBars.length])

  const sortedSnackBars = snackBars
    .slice()
    .sort(
      (a, b) =>
        new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
    )

  return createPortal(
    <aside
      aria-label="Zone de notifications"
      className={cn(
        styles['snack-bar-container'],
        isStickyBarOpen && styles['with-sticky-action-bar']
      )}
    >
      {/*
        The `role=alert` block should always be present for the announcer to watch its changes and read them.
      */}
      <div className={styles['visually-hidden']}>
        <div role="alert" aria-live="assertive" aria-atomic="true">
          {sortedSnackBars.length > 0 ? (
            sortedSnackBars.map((snackBar) => (
              // Utiliser impérativement l'id unique pour forcer le re-rendu du nœud DOM
              <div key={snackBar.id}>
                {getSnackBarAnnouncement(
                  snackBar.variant,
                  snackBar.description
                )}
              </div>
            ))
          ) : (
            <div>&nbsp;</div>
          )}
        </div>
      </div>
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
    </aside>,
    portalTarget
  )
}
