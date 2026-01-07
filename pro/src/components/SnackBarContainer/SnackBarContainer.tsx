import cn from 'classnames'

import { useAppDispatch } from '@/commons/hooks/useAppDispatch'
import { useAppSelector } from '@/commons/hooks/useAppSelector'
import { useMediaQuery } from '@/commons/hooks/useMediaQuery'
import { removeSnackBar } from '@/commons/store/snackBar/reducer'
import {
  isStickyBarOpenSelector,
  listSelector,
} from '@/commons/store/snackBar/selectors'
import { SnackBar } from '@/design-system/SnackBar/SnackBar'

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
  const isSmallScreen = useMediaQuery('(max-width: 38.125rem)')

  // Small (mobile/app): the last snackbar appears below the first one (ascending order)
  // Large (desktop/tablet): the last snackbar appears above the first one (descending order)
  const snackBarsToDisplay = snackBars.sort(
    (a, b) =>
      (isSmallScreen ? 1 : -1) *
      (new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime())
  )

  return (
    <div
      className={cn(
        styles['snack-bar-container'],
        isStickyBarOpen && styles['with-sticky-action-bar']
      )}
    >
      {snackBarsToDisplay.map((snackBar, index) => (
        <SnackBar
          key={snackBar.id}
          variant={snackBar.variant}
          text={snackBar.text}
          onClose={() => dispatch(removeSnackBar(snackBar.id))}
          testId={`global-snack-bar-${snackBar.variant}-${index}`}
        />
      ))}
    </div>
  )
}
