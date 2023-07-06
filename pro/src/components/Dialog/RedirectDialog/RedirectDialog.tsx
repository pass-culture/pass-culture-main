import React, { FunctionComponent, SVGProps } from 'react'

import { ReactComponent as FullLinkIcon } from 'icons/full-link.svg'
import { ReactComponent as FullNextIcon } from 'icons/full-next.svg'
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
  cancelIcon?: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
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
          Icon={withRedirectLinkIcon ? FullLinkIcon : undefined}
        >
          {redirectText}
        </ButtonLink>

        <Button
          Icon={cancelIcon || FullNextIcon}
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
