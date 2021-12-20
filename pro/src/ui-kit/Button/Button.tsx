/* eslint-disable react/button-has-type */
import cn from 'classnames'
import React from 'react'

import styles from './Button.module.scss'
import { SharedButtonProps, ButtonVariant } from './types'

interface IButtonProps
  extends SharedButtonProps,
    React.HTMLProps<HTMLButtonElement> {
  type?: 'button' | 'submit'
  ref?: React.RefObject<HTMLButtonElement>
}

const Button = ({
  className,
  children,
  Icon,
  ref,
  variant = ButtonVariant.PRIMARY,
  type = 'button',
  ...buttonAttrs
}: IButtonProps): JSX.Element => (
  <button
    className={cn(styles['button'], styles[`button-${variant}`], className)}
    ref={ref}
    type={type}
    {...buttonAttrs}
  >
    {Icon && <Icon />}
    {children}
  </button>
)

Button.variant = ButtonVariant

export default Button
