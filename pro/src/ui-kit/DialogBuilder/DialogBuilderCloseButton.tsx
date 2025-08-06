import * as Dialog from '@radix-ui/react-dialog'
import classNames from 'classnames'

import strokeCloseIcon from '@/icons/stroke-close.svg'
import { SvgIcon } from '@/ui-kit/SvgIcon/SvgIcon'

import styles from './DialogBuilder.module.scss'

/**
 * Props for the DialogBuilderCloseButton component.
 */
type DialogBuilderCloseButtonProps = {
  /**
   * Callback function triggered when the close button is clicked.
   */
  onCloseClick?: () => void
  /**
   * Custom CSS class for additional styling of the close button.
   */
  closeButtonClassName?: string
}

/**
 * The DialogBuilderCloseButton component is used to provide a close button for the dialog.
 * It allows users to close the dialog by clicking the button, which includes an icon.
 *
 * ---
 * **Important: Use the `onCloseClick` prop to handle additional actions when the close button is clicked.**
 * ---
 *
 * @param {DialogBuilderCloseButtonProps} props - The props for the DialogBuilderCloseButton component.
 * @returns {JSX.Element} The rendered DialogBuilderCloseButton component.
 *
 * @example
 * <DialogBuilderCloseButton onCloseClick={() => console.log('Dialog closed')} />
 *
 * @accessibility
 * - **Close Button Label**: The close button includes a `title` attribute with the text "Fermer la modale" to provide additional context for screen readers.
 * - **Icon Usage**: The close button includes an icon to visually indicate its purpose, which helps users quickly understand its functionality.
 */
export const DialogBuilderCloseButton = ({
  onCloseClick,
  closeButtonClassName,
}: DialogBuilderCloseButtonProps): JSX.Element => (
  <div className={styles['dialog-builder-close-container']}>
    <Dialog.Close
      className={classNames(
        styles['dialog-builder-close'],
        closeButtonClassName
      )}
      onClick={onCloseClick}
      type="button"
    >
      <SvgIcon
        src={strokeCloseIcon}
        alt="Fermer la fenêtre modale"
        className={styles['dialog-builder-close-icon']}
      />
    </Dialog.Close>
  </div>
)
