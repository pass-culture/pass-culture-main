import { useId } from 'react'

import { BaseDialog } from '@/ui-kit/BaseDialog/BaseDialog'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './SimpleModal.module.scss'

export interface SimpleModalProps {
  /**
   * The heading title of the dialog.
   */
  title: string
  /**
   * An icon path.
   */
  iconPath?: string
  /**
   * The content to be displayed inside the dialog.
   */
  children: React.ReactNode
  /**
   * Function called to close the modal.
   */
  onClose: () => void
  /**
   * Controls the open state of the dialog.
   */
  isOpen: boolean
  /**
   * Action buttons to be displayed at the bottom of the dialog. The dialog must not have more than 3 buttons.
   */
  actionButtons?: React.ReactNode
  /**
   * Identifier of the description element for screen readers (aria-describedby).
   */
  ariaDescribedBy?: string
}

export const SimpleModal = ({
  title,
  iconPath,
  children,
  onClose,
  isOpen,
  actionButtons,
  ariaDescribedBy,
}: Readonly<SimpleModalProps>) => {
  const dialogTitleId = useId()

  return (
    <BaseDialog
      isOpen={isOpen}
      onClose={onClose}
      ariaLabelledBy={dialogTitleId}
      ariaDescribedBy={ariaDescribedBy}
      variant="simple"
    >
      <div className={styles['dialog-container']}>
        {iconPath && (
          <SvgIcon alt="" src={iconPath} width="88" data-testid="modal-icon" />
        )}
        <div className={styles['dialog-content']}>
          <h1 className={styles['dialog-content-title']} id={dialogTitleId}>
            {title}
          </h1>
          <div>{children}</div>
        </div>
        <div className={styles['action-buttons']}>{actionButtons}</div>
      </div>
    </BaseDialog>
  )
}
