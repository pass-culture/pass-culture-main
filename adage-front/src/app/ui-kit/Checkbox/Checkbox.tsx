import cn from 'classnames'
import React from 'react'

import './Checkbox.scss'

interface IBaseCheckboxProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  label: string
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
  <label className={cn('base-checkbox', className)}>
    <input
      type="checkbox"
      {...props}
      className={cn('base-checkbox-input', {
        'has-error': hasError,
      })}
    />
    {!!Icon && (
      <span className="base-checkbox-icon">
        <Icon />
      </span>
    )}
    <span className="base-checkbox-label">{label}</span>
  </label>
)

export default BaseCheckbox
