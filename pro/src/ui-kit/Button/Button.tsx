import cn from 'classnames'
import React from 'react'

import styles from './Button.module.scss'
import { ButtonVariant, IconPositionEnum, SharedButtonProps } from './types'

interface IButtonProps
  extends SharedButtonProps,
    React.HTMLProps<HTMLButtonElement> {
  type?: 'button' | 'submit'
  innerRef?: React.RefObject<HTMLButtonElement>
  className?: string
}

const Button = ({
  className,
  children,
  Icon,
  iconPosition = IconPositionEnum.LEFT,
  variant = ButtonVariant.PRIMARY,
  type = 'button',
  innerRef,
  ...buttonAttrs
}: IButtonProps): JSX.Element => (
  <button
    className={cn(styles['button'], styles[`button-${variant}`], className)}
    ref={innerRef}
    type={type}
    {...buttonAttrs}
  >
    {Icon && iconPosition === IconPositionEnum.LEFT && (
      <Icon className={cn(styles['button-icon'], styles['button-icon-left'])} />
    )}
    {children}
    {Icon && iconPosition === IconPositionEnum.RIGHT && (
      <Icon
        className={cn(styles['button-icon'], styles['button-icon-right'])}
      />
    )}
  </button>
)

export default Button
