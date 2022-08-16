import cn from 'classnames'
import React from 'react'

import './Checkbox.scss'

interface IBaseCheckboxProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string | React.ReactNode
  hasError?: boolean
  className?: string
  Icon?: React.FunctionComponent<
    React.SVGProps<SVGSVGElement> & {
      title?: string | undefined
    }
  >
}

const BaseCheckbox = ({
  label,
  hasError,
  className,
  Icon,
  ...props
}: IBaseCheckboxProps): JSX.Element => (
  <div className={cn('base-checkbox', className)}>
    <input
      type="checkbox"
      {...props}
      className={cn('base-checkbox-input', {
        'has-error': hasError,
      })}
      id={props.name}
    />
    {!!Icon && (
      <span className="base-checkbox-icon">
        <Icon />
      </span>
    )}
    <label className="base-checkbox-label" htmlFor={props.name}>
      {label}
    </label>
  </div>
)

export default BaseCheckbox
