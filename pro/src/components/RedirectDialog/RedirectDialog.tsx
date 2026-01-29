import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import fullNextIcon from '@/icons/full-next.svg'

import { Dialog, type DialogProps } from '../Dialog/Dialog'
import styles from './RedirectDialog.module.scss'

type RedirectDialogProps = DialogProps & {
  redirectText: string
  to: string
  isExternal: boolean
  cancelText: string
  onCancel: () => void
  onRedirect?: () => void
  withRedirectLinkIcon?: boolean
  cancelIcon?: string
}

export const RedirectDialog = ({
  title,
  secondTitle,
  children,
  icon,
  hideIcon = false,
  extraClassNames,
  redirectText,
  to,
  isExternal,
  cancelIcon,
  onRedirect,
  cancelText,
  onCancel,
  onClose,
  withRedirectLinkIcon = true,
  open,
}: RedirectDialogProps): JSX.Element => {
  return (
    <Dialog
      onCancel={onCancel}
      onClose={onClose}
      title={title}
      secondTitle={secondTitle}
      icon={icon}
      hideIcon={hideIcon}
      explanation={children}
      extraClassNames={`${extraClassNames} ${styles['confirm-dialog-explanation']}`}
      open={open}
    >
      <div className={styles['redirect-dialog-actions']}>
        <Button
          as="a"
          to={to}
          data-testid="redirect-dialog-link"
          isExternal={isExternal}
          variant={ButtonVariant.PRIMARY}
          onClick={onRedirect}
          icon={withRedirectLinkIcon ? fullLinkIcon : undefined}
          label={redirectText}
        />

        <Button
          icon={cancelIcon || fullNextIcon}
          onClick={() => {
            onCancel()
          }}
          data-testid="redirect-dialog-button-cancel"
          variant={ButtonVariant.TERTIARY}
          color={ButtonColor.NEUTRAL}
          label={cancelText}
        />
      </div>
    </Dialog>
  )
}
