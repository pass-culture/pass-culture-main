import cn from 'classnames'
import React from 'react'
import './Button.scss'

interface IButton {
  onClick: () => void
  className?: string
  label?: string
  disabled?: boolean
  variant?: 'primary' | 'secondary'
}

const Button = ({
  className,
  onClick,
  label,
  disabled = false,
  variant = 'primary',
}: IButton): JSX.Element => {
  return (
    <button
      className={cn('button', className, {
        'button-primary': variant === 'primary',
        'button-secondary': variant === 'secondary',
      })}
      disabled={disabled}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  )
}

export default Button
