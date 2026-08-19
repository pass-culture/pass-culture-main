import { useId } from 'react'

import {
  TABLET_MEDIA_QUERY,
  useMediaQuery,
} from '@/commons/hooks/useMediaQuery'
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
  actionButtons?: React.ReactNode[]
  /**
   * Identifier of the description element for screen readers (aria-describedby).
   */
  ariaDescribedBy?: string
  /**
   * Element to focus after the dialog has closed.
   * Native `<dialog>` already restores focus to the opener; use this to
   * override that target (e.g. a dropdown trigger instead of a menu item).
   */
  refToFocusOnClose?: React.RefObject<HTMLElement | null>
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
  refToFocusOnClose,
}: Readonly<SimpleModalProps>) => {
  const dialogTitleId = useId()
  const isSmallScreen = useMediaQuery(TABLET_MEDIA_QUERY)
  const orderedButtons =
    isSmallScreen && actionButtons
      ? [...actionButtons].reverse()
      : actionButtons

  return (
    <BaseDialog
      isOpen={isOpen}
      onClose={onClose}
      ariaLabelledBy={dialogTitleId}
      ariaDescribedBy={ariaDescribedBy}
      refToFocusOnClose={refToFocusOnClose}
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
          <div className={styles['action-buttons']}>{orderedButtons}</div>
        </div>
      </div>
    </BaseDialog>
  )
}
