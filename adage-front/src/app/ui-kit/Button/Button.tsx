import cn from 'classnames'
import React from 'react'

import './Button.scss'
import { ReactComponent as SpinnerIcon } from 'assets/loader.svg'

interface IButton extends React.HTMLProps<HTMLButtonElement> {
  label?: string
  variant?: 'primary' | 'secondary'
  isLoading?: boolean
}

const Button = ({
  className,
  label,
  variant = 'primary',
  isLoading,
  ...props
}: IButton): JSX.Element => {
  return (
    <button
      className={cn('button', className, {
        'button-primary': variant === 'primary',
        'button-secondary': variant === 'secondary',
        'button-is-loading': isLoading,
      })}
      {...props}
      type="button"
    >
      {isLoading ? <SpinnerIcon className="button-spinner" /> : label}
    </button>
  )
}

export default Button
