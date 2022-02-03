import cn from 'classnames'
import React, { FunctionComponent, SVGProps } from 'react'

import './Button.scss'
import { ReactComponent as SpinnerIcon } from 'assets/loader.svg'

interface IButton extends React.HTMLProps<HTMLButtonElement> {
  label?: string
  variant?: 'primary' | 'secondary'
  isLoading?: boolean
  Icon?: FunctionComponent<
    SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
  classNameIcon?: string
}

const Button = ({
  Icon,
  classNameIcon,
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
      {Icon && <Icon className={classNameIcon} />}
      {isLoading ? <SpinnerIcon className="button-spinner" /> : label}
    </button>
  )
}

export default Button
