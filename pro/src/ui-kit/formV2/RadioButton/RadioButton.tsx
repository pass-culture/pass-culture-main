import cn from 'classnames'
import React, { ForwardedRef, forwardRef } from 'react'

import {
  BaseRadio,
  BaseRadioProps,
  RadioVariant,
} from 'ui-kit/form/shared/BaseRadio/BaseRadio'

/**
 * Props for the RadioButton component.
 *
 * @extends Partial<React.InputHTMLAttributes<HTMLInputElement>>
 */
export interface RadioButtonProps
  extends Partial<React.InputHTMLAttributes<HTMLInputElement>> {
  name: string
  label: string | JSX.Element
  value: string
  variant?: RadioVariant
  hasError?: boolean
  checked?: boolean
  ariaDescribedBy?: string
  childrenOnChecked?: JSX.Element
  icon?: BaseRadioProps['icon']
  iconPosition?: BaseRadioProps['iconPosition']
  description?: BaseRadioProps['description']
}

export const RadioButton = forwardRef(
  (
    {
      disabled,
      name,
      label,
      value,
      variant,
      className,
      hasError,
      checked,
      ariaDescribedBy,
      childrenOnChecked,
      icon,
      iconPosition,
      description,
      ...props
    }: RadioButtonProps,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    return (
      <BaseRadio
        ref={ref}
        {...props}
        name={name}
        disabled={disabled}
        id={name}
        label={label}
        value={value}
        className={cn(className)}
        checked={checked}
        hasError={hasError}
        variant={variant}
        ariaDescribedBy={ariaDescribedBy}
        childrenOnChecked={childrenOnChecked}
        icon={icon}
        iconPosition={iconPosition}
        description={description}
      />
    )
  }
)

RadioButton.displayName = 'RadioButton'
