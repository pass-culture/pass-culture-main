import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullLinkIcon from '@/icons/full-link.svg'
import fullNextIcon from '@/icons/full-next.svg'
import type { LinkProps } from '@/ui-kit/Button/ButtonLink'

import { Dialog, type DialogProps } from '../Dialog/Dialog'
import styles from './RedirectDialog.module.scss'

type RedirectDialogProps = DialogProps & {
  redirectText: string
  redirectLink: LinkProps
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
  redirectLink,
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
          data-testid="redirect-dialog-link"
          {...redirectLink}
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
