import * as Dialog from '@radix-ui/react-dialog'
import cn from 'classnames'

import styles from './DialogBuilder.module.scss'
import { DialogBuilderCloseButton } from './DialogBuilderCloseButton'

export type DialogVariant = 'default' | 'drawer'

/**
 * Props for the DialogBuilder component.
 */
type DialogBuilderProps = {
  /**
   * The trigger element that opens the dialog.
   */
  trigger?: React.ReactNode
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
  children,
  defaultOpen = false,
  onOpenChange,
  open,
  closeButtonClassName,
  className,
  variant = 'default',
}: DialogBuilderProps) {
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
        >
          <Dialog.Content
            className={cn(styles['dialog-builder-content'], className)}
            aria-describedby={undefined}
          >
            <DialogBuilderCloseButton
              closeButtonClassName={closeButtonClassName}
            />
            <section>{children}</section>
          </Dialog.Content>
        </Dialog.Overlay>
      </Dialog.Portal>
    </Dialog.Root>
  )
}
