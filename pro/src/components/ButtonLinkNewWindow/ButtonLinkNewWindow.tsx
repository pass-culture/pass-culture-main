import React, { FunctionComponent, useCallback, MouseEventHandler } from 'react'

import { ButtonLink } from 'ui-kit'
import { ButtonVariant, SharedButtonProps } from 'ui-kit/Button/types'

export interface IButtonLinkNewWindowProps extends SharedButtonProps {
  className?: string
  linkTo: string
  children?: React.ReactNode
  tracking?: { isTracked: boolean; trackingFunction: () => void }
}

export const ButtonLinkNewWindow: FunctionComponent<
  IButtonLinkNewWindowProps
> = ({
  className,
  linkTo,
  children,
  tracking,
  Icon,
  variant = ButtonVariant.TERNARY,
}) => {
  const openWindow: MouseEventHandler = useCallback(
    event => {
      event.preventDefault()

      window
        .open(linkTo, 'targetWindow', 'toolbar=no, width=375, height=667')
        ?.focus()

      if (tracking?.isTracked) {
        tracking.trackingFunction()
      }
    },
    [linkTo]
  )

  return (
    <ButtonLink
      className={className}
      link={{ to: linkTo, isExternal: true }}
      Icon={Icon}
      onClick={openWindow}
      variant={variant}
    >
      {children}
    </ButtonLink>
  )
}
