import React, { FunctionComponent, useCallback, MouseEventHandler } from 'react'

import { ButtonLink } from 'ui-kit'
import { ButtonVariant, SharedButtonProps } from 'ui-kit/Button/types'

interface ButtonLinkNewWindowProps extends SharedButtonProps {
  className?: string
  linkTo: string
  children?: React.ReactNode
  svgAlt?: string
}

export const ButtonLinkNewWindow: FunctionComponent<
  ButtonLinkNewWindowProps
> = ({
  className,
  linkTo,
  children,
  icon,
  variant = ButtonVariant.TERNARY,
  svgAlt,
}) => {
  const openWindow: MouseEventHandler = useCallback(
    event => {
      event.preventDefault()

      window
        .open(linkTo, 'targetWindow', 'toolbar=no, width=375, height=667')
        ?.focus()
    },
    [linkTo]
  )

  return (
    <ButtonLink
      className={className}
      link={{ to: linkTo, isExternal: true }}
      icon={icon}
      onClick={openWindow}
      variant={variant}
      svgAlt={svgAlt}
    >
      {children}
    </ButtonLink>
  )
}
