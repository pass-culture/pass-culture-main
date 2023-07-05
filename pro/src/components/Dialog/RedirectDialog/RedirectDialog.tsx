import React from 'react'

import fullLinkIcon from 'icons/full-link.svg'
import fullNextIcon from 'icons/full-next.svg'
import { Button, ButtonLink } from 'ui-kit'
import { LinkProps } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import Dialog, { DialogProps } from '../Dialog'

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

const RedirectDialog = ({
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
  withRedirectLinkIcon = true,
}: RedirectDialogProps): JSX.Element => {
  return (
    <Dialog
      onCancel={onCancel}
      title={title}
      secondTitle={secondTitle}
      icon={icon}
      hideIcon={hideIcon}
      explanation={children}
      extraClassNames={`${extraClassNames} ${styles['confirm-dialog-explanation']}`}
    >
      <div className={styles['redirect-dialog-actions']}>
        <ButtonLink
          data-testid="redirect-dialog-link"
          link={redirectLink}
          variant={ButtonVariant.PRIMARY}
          onClick={onRedirect}
          icon={withRedirectLinkIcon ? fullLinkIcon : undefined}
        >
          {redirectText}
        </ButtonLink>

        <Button
          icon={cancelIcon || fullNextIcon}
          onClick={() => {
            onCancel()
          }}
          data-testid="redirect-dialog-button-cancel"
          variant={ButtonVariant.TERNARY}
          className={styles['redirect-dialog-cancel-button']}
        >
          {cancelText}
        </Button>
      </div>
    </Dialog>
  )
}

export default RedirectDialog
