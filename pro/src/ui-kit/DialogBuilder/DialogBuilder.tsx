import * as Dialog from '@radix-ui/react-dialog'

import styles from './DialogBuilder.module.scss'
import { DialogBuilderCloseButton } from './DialogBuilderCloseButton'

type DialogBuilderProps = {
  trigger?: React.ReactNode
  children: React.ReactNode
  defaultOpen?: boolean
  onOpenChange?: (open: boolean) => void
  open?: boolean
  closeButtonClassName?: string
}

export function DialogBuilder({
  trigger,
  children,
  defaultOpen = false,
  onOpenChange,
  open,
  closeButtonClassName,
}: DialogBuilderProps) {
  return (
    <Dialog.Root
      defaultOpen={defaultOpen}
      onOpenChange={onOpenChange}
      open={open}
    >
      {trigger && <Dialog.Trigger asChild>{trigger}</Dialog.Trigger>}
      <Dialog.Portal>
        <Dialog.Overlay className={styles['dialog-builder-overlay']}>
          <Dialog.Content
            className={styles['dialog-builder-content']}
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
