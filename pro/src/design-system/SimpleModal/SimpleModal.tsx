import { useId } from 'react'

import fullCloseIcon from '@/icons/full-close.svg'
import { BaseDialog } from '@/ui-kit/BaseDialog/BaseDialog'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import { Button } from '../Button/Button'
import { ButtonColor, ButtonVariant } from '../Button/types'
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
   * Optional className applied to the icon.
   */
  iconClassName?: string
  /**
   * The content to be displayed inside the dialog.
   */
  children?: React.ReactNode
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
  iconClassName,
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
    >
      <div className={styles['dialog-wrapper']}>
        <span className={styles['close-button']}>
          <Button
            icon={fullCloseIcon}
            variant={ButtonVariant.TERTIARY}
            color={ButtonColor.NEUTRAL}
            onClick={onClose}
            aria-label={'Fermer la boite de dialogue'}
          />
        </span>
        <div className={styles['dialog-container']}>
          {iconPath && (
            <SvgIcon
              alt=""
              src={iconPath}
              className={iconClassName}
              width="88"
              data-testid="modal-icon"
            />
          )}
          <div className={styles['dialog-content']}>
            <h1 className={styles['dialog-content-title']} id={dialogTitleId}>
              {title}
            </h1>
            {children && <div>{children}</div>}
          </div>
          <div className={styles['action-buttons']}>{actionButtons}</div>
        </div>
      </div>
    </BaseDialog>
  )
}
