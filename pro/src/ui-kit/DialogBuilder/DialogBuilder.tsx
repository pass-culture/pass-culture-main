import * as Dialog from '@radix-ui/react-dialog'
import cn from 'classnames'

import styles from './DialogBuilder.module.scss'
import { DialogBuilderCloseButton } from './DialogBuilderCloseButton'

type DialogBuilderProps = {
  trigger?: React.ReactNode
  children: React.ReactNode
  defaultOpen?: boolean
  onOpenChange?: (open: boolean) => void
  open?: boolean
  closeButtonClassName?: string
  className?: string
}

export function DialogBuilder({
  trigger,
  children,
  defaultOpen = false,
  onOpenChange,
  open,
  closeButtonClassName,
  className,
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
