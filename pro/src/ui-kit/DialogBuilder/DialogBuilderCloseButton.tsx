import * as Dialog from '@radix-ui/react-dialog'

import strokeCloseIcon from 'icons/stroke-close.svg'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import styles from './DialogBuilder.module.scss'

type DialogBuilderCloseButtonProps = {
  onCloseClick?: () => void
  className?: string
}

export const DialogBuilderCloseButton = ({
  onCloseClick,
}: DialogBuilderCloseButtonProps): JSX.Element => (
  <div className={styles['dialog-builder-close-container']}>
    <Dialog.Close
      className={styles['dialog-builder-close']}
      onClick={onCloseClick}
      title="Fermer la modale"
      type="button"
    >
      <SvgIcon
        src={strokeCloseIcon}
        alt=""
        className={styles['dialog-builder-close-icon']}
      />
    </Dialog.Close>
  </div>
)
