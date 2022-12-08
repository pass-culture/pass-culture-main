import React, { FunctionComponent, SVGProps } from 'react'

import { ExternalLinkIcon } from 'icons'
import { ReactComponent as AlertSvg } from 'icons/ico-alert-grey.svg'
import { ReactComponent as ArrowIcon } from 'icons/ico-right-circle-arrow.svg'
import { Button, ButtonLink } from 'ui-kit'
import { LinkProps } from 'ui-kit/Button/ButtonLink'
import { ButtonVariant } from 'ui-kit/Button/types'

import Dialog, { IDialogProps } from '../Dialog'

import styles from './RedirectDialog.module.scss'

type IRedirectDialogProps = IDialogProps & {
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
  withRedirectLinkIcon = true,
  cancelIcon,
  onRedirect,
  cancelText,
  onCancel,
}: IRedirectDialogProps): JSX.Element => {
  return (
    <Dialog
      onCancel={onCancel}
      title={title}
      secondTitle={secondTitle}
      icon={icon ?? AlertSvg}
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
          Icon={withRedirectLinkIcon ? ExternalLinkIcon : undefined}
        >
          {redirectText}
        </ButtonLink>

        <Button
          Icon={cancelIcon || ArrowIcon}
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
