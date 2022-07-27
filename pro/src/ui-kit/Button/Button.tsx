import cn from 'classnames'
import React from 'react'

import styles from './Button.module.scss'
import { ButtonVariant, SharedButtonProps } from './types'

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
    {Icon && <Icon className={styles['button-icon']} />}
    {children}
  </button>
)

export default Button
