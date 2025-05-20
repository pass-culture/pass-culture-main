import * as Dialog from '@radix-ui/react-dialog'
import cn from 'classnames'
import { useRef } from 'react'

import styles from './DialogBuilder.module.scss'
import { DialogBuilderCloseButton } from './DialogBuilderCloseButton'

type DialogVariant = 'default' | 'drawer'

/**
 * Props for the DialogBuilder component.
 */
export type DialogBuilderProps = {
  /**
   * The trigger element that opens the dialog.
   */
  trigger?: React.ReactNode
  /**
   * The heading title of the dialog.
   */
  title?: string
  /**
   * The content to be displayed inside the dialog.
   */
  children: React.ReactNode
  /**
   * Determines if the dialog is open by default.
   * @default false
   */
  defaultOpen?: boolean
  /**
   * Callback function triggered when the open state of the dialog changes.
   */
  onOpenChange?: (open: boolean) => void
  /**
   * Controls the open state of the dialog.
   */
  open?: boolean
  /**
   * Custom CSS class for additional styling of the close button.
   */
  closeButtonClassName?: string
  /**
   * Custom CSS class for additional styling of the dialog content.
   */
  className?: string
  variant?: DialogVariant
  /**
   * Ref of the element to focus on when the dialog is closed.
   * If refToFocusOnClose.current is null, the trigger element will be focused as a fallback.
   */
  refToFocusOnClose?: React.RefObject<HTMLElement>
}

/**
 * The DialogBuilder component is used to create a customizable dialog box.
 * It includes support for a trigger button, customizable content, and an optional close button.
 *
 * ---
 * **Important: Use the `trigger` prop to specify the element that should open the dialog.**
 * ---
 *
 * @param {DialogBuilderProps} props - The props for the DialogBuilder component.
 * @returns {JSX.Element} The rendered DialogBuilder component.
 *
 * @example
 * <DialogBuilder trigger={<button>Open Dialog</button>}>
 *   <p>This is the content inside the dialog.</p>
 * </DialogBuilder>
 *
 * @accessibility
 * - **Keyboard Navigation**: When using the trigger prop along with the `<Dialog.Close>` tag
 * around dialog validation buttons, the trigger button will automatically be re-focused on close.
 */
export function DialogBuilder({
  trigger,
  title,
  children,
  defaultOpen = false,
  onOpenChange,
  open,
  closeButtonClassName,
  className,
  variant = 'default',
  refToFocusOnClose,
}: DialogBuilderProps) {
  const contentRef = useRef<HTMLDivElement>(null)
  return (
    <Dialog.Root
      defaultOpen={defaultOpen}
      onOpenChange={onOpenChange}
      open={open}
    >
      {trigger && <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>}
      <Dialog.Portal>
        <Dialog.Overlay
          className={cn(
            styles['dialog-builder-overlay'],
            styles[`dialog-builder-overlay-${variant}`]
          )}
          data-testid="dialog-overlay"
        >
          <Dialog.Content
            className={cn(styles['dialog-builder-content'], className)}
            aria-describedby={undefined}
            ref={contentRef}
            onPointerDownOutside={(e) => {
              if (!contentRef.current) {
                return
              }
              const contentRect = contentRef.current.getBoundingClientRect()
              // Detect if click actually happened within the bounds of content.
              // This can happen if click was on an absolutely positioned element overlapping content,
              // such as a click on the scroll bar (https://github.com/radix-ui/primitives/issues/1280)
              /* istanbul ignore next */
              const actuallyClickedInside =
                e.detail.originalEvent.clientX > contentRect.left &&
                e.detail.originalEvent.clientX <
                  contentRect.left + contentRect.width &&
                e.detail.originalEvent.clientY > contentRect.top &&
                e.detail.originalEvent.clientY <
                  contentRect.top + contentRect.height
              if (actuallyClickedInside) {
                e.preventDefault()
              }
            }}
            onCloseAutoFocus={(ev: any) => {
              ev.preventDefault()

              if (!refToFocusOnClose) {
                return
              }

              refToFocusOnClose.current?.focus()
            }}
          >
            <DialogBuilderCloseButton
              closeButtonClassName={closeButtonClassName}
            />
            <section className={styles['dialog-builder-section']}>
              {title && (
                <Dialog.Title asChild>
                  <h1 className={styles['dialog-builder-title']}>{title}</h1>
                </Dialog.Title>
              )}
              {children}
            </section>
          </Dialog.Content>
        </Dialog.Overlay>
      </Dialog.Portal>
    </Dialog.Root>
  )
}

function DialogBuilderFooter({ children }: { children: React.ReactNode }) {
  return <div className={styles['dialog-builder-footer']}>{children}</div>
}

DialogBuilder.Footer = DialogBuilderFooter
