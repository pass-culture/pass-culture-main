import type React from 'react'
import { useEffect, useRef } from 'react'

import styles from './BaseDialog.module.scss'

export interface BaseDialogProps {
  /**
   * Determines whether the modal is open or closed.
   */
  isOpen: boolean
  /**
   * Callback triggered to close the modal (Escape key, backdrop click, etc.).
   * It is up to the parent to update the `isOpen` state in return.
   */
  onClose: () => void
  /**
   * Identifier of the modal's title element for screen readers (aria-labelledby).
   */
  ariaLabelledBy?: string
  /**
   * Identifier of the description element for screen readers (aria-describedby).
   */
  ariaDescribedBy?: string
  /**
   * Modal content.
   */
  children: React.ReactNode
  /**
   * Element to focus after the dialog has closed.
   * Native `<dialog>` already restores focus to the opener; use this to
   * override that target (e.g. a dropdown trigger instead of a menu item).
   */
  refToFocusOnClose?: React.RefObject<HTMLElement | null>
  /**
   * When true, marks this dialog as an eligible target for the snackbar portal.
   * Only set on DetailedModal — not on SimpleModal / navigation guard dialogs.
   */
  isSnackBarPortalTarget?: boolean
}

/**
 * Base component wrapping the native HTML5 `<dialog>` element.
 * It handles open state synchronization, keyboard accessibility (Escape),
 * the native focus trap, and closing on backdrop click.
 *
 * This component does not embed any complex visual style (borders, backgrounds, paddings)
 * so as to provide a neutral base for specialized modals (SimpleModal, DetailedModal).
 */
export const BaseDialog = ({
  isOpen,
  onClose,
  ariaLabelledBy,
  ariaDescribedBy,
  children,
  refToFocusOnClose,
  isSnackBarPortalTarget = false,
}: BaseDialogProps): JSX.Element => {
  const dialogRef = useRef<HTMLDialogElement>(null)

  // Synchronizes React's open/closed state with the imperative APIs of the <dialog> tag
  useEffect(() => {
    const dialog = dialogRef.current
    if (!dialog) return

    if (isOpen) {
      if (!dialog.open) {
        dialog.showModal()
      }
    } else if (dialog.open) {
      dialog.close()
    }
  }, [isOpen])

  // Prevents the browser's default auto-close behavior
  // so that React controls the state via the `onClose` callback
  const handleCancel = (e: React.SyntheticEvent<HTMLDialogElement>) => {
    e.preventDefault()
    onClose()
  }

  // Close on backdrop click (Light Dismiss)
  const handleBackdropClick = (e: React.MouseEvent<HTMLDialogElement>) => {
    const dialog = dialogRef.current
    if (!dialog || e.target !== dialog) return

    const rect = dialog.getBoundingClientRect()
    const isClickInside =
      rect.top <= e.clientY &&
      e.clientY <= rect.top + rect.height &&
      rect.left <= e.clientX &&
      e.clientX <= rect.left + rect.width

    if (!isClickInside) {
      onClose()
    }
  }

  // Native `close` is queued after dialog.close() (focus trap already gone).
  const handleNativeClose = () => {
    refToFocusOnClose?.current?.focus()
  }

  return (
    // biome-ignore lint/a11y/useKeyWithClickEvents: backdrop click is pointer-only; keyboard dismissal is handled via onCancel (Escape)
    <dialog
      ref={dialogRef}
      onCancel={handleCancel}
      onClick={handleBackdropClick}
      onClose={handleNativeClose}
      aria-labelledby={ariaLabelledBy}
      aria-describedby={ariaDescribedBy}
      className={styles['base-dialog']}
      data-snackbar-portal={isSnackBarPortalTarget ? '' : undefined}
    >
      {children}
    </dialog>
  )
}
