import classNames from 'classnames'
import { useId, useState } from 'react'

import { Checkbox, CheckboxProps } from '../Checkbox/Checkbox'

import styles from './CheckboxGroup.module.scss'

type CheckboxGroupOptionSimple = Omit<
  CheckboxProps,
  'checked' | 'onChange' | 'hasError' | 'disabled' | 'variant' | 'asset'
> & {
  label: string
  value: string | number
  variant?: 'default'
  asset?: never
}

type CheckboxGroupOptionDetailed = Omit<
  CheckboxProps,
  'checked' | 'onChange' | 'hasError' | 'disabled' | 'variant'
> & {
  label: string
  value: string | number
  variant: 'detailed'
  asset?: CheckboxProps['asset']
}

export type CheckboxGroupOption =
  | CheckboxGroupOptionSimple
  | CheckboxGroupOptionDetailed

type CheckboxGroupProps = {
  label: string
  description?: string
  error?: string
  options: CheckboxGroupOption[]
  value?: (string | number)[]
  defaultValue?: (string | number)[]
  onChange?: (value: (string | number)[]) => void
  display?: 'vertical' | 'horizontal'
  variant?: 'default' | 'detailed'
  disabled?: boolean
}

export const CheckboxGroup = ({
  label,
  description,
  error,
  options,
  value,
  defaultValue,
  onChange,
  display = 'vertical',
  variant = 'default',
  disabled = false,
}: CheckboxGroupProps) => {
  if (options.length < 2) {
    throw new Error('CheckboxGroup requires at least two options.')
  }

  const labelId = useId()
  const errorId = useId()
  const descriptionId = useId()
  const describedBy = [
    error ? errorId : null,
    description ? descriptionId : null,
  ]
    .filter(Boolean)
    .join(' ')

  // Controlled / Uncontrolled
  const isControlled = value !== undefined
  const [internalValue, setInternalValue] = useState<(string | number)[]>(
    defaultValue ?? []
  )
  const selectedValues = isControlled ? value! : internalValue

  const handleChange = (optionValue: string | number) => {
    let newValues: (string | number)[]
    if (selectedValues.includes(optionValue)) {
      newValues = selectedValues.filter((v) => v !== optionValue)
    } else {
      newValues = [...selectedValues, optionValue]
    }
    if (!isControlled) {
      setInternalValue(newValues)
    }
    onChange?.(newValues)
  }

  const propagateAsset =
    variant === 'detailed' && options.some((opt) => 'asset' in opt && opt.asset)

  return (
    <div
      role="group"
      aria-labelledby={labelId}
      aria-describedby={describedBy || undefined}
      className={classNames(
        styles['checkbox-group'],
        styles[`display-${display}`],
        styles[`variant-${variant}`],
        { [styles['disabled']]: disabled }
      )}
    >
      <div className={styles['checkbox-group-header']}>
        <span
          id={labelId}
          className={classNames(styles['checkbox-group-label'], {
            [styles['disabled']]: disabled,
          })}
        >
          {label}
        </span>
        {description && (
          <span
            id={descriptionId}
            className={classNames(styles['checkbox-group-description'], {
              [styles['disabled']]: disabled,
            })}
          >
            {description}
          </span>
        )}
        <div role="alert" id={errorId}>
          {error && (
            <span className={styles['checkbox-group-error']}>{error}</span>
          )}
        </div>
      </div>
      <div className={styles['checkbox-group-options']}>
        {options.map((option) => {
          const checked = selectedValues.includes(option.value)

          const detailedProps: Record<string, any> =
            option.variant === 'detailed'
              ? {
                  description: option.description,
                  asset: propagateAsset ? option.asset : undefined,
                  collapsed: option.collapsed,
                }
              : {}

          return (
            <Checkbox
              key={option.value}
              label={option.label}
              checked={checked}
              onChange={() => handleChange(option.value)}
              hasError={!!error}
              disabled={disabled}
              sizing={option.sizing}
              indeterminate={option.indeterminate}
              name={option.name}
              required={option.required}
              asterisk={option.asterisk}
              onBlur={option.onBlur}
              variant={option.variant}
              {...detailedProps}
            />
          )
        })}
      </div>
    </div>
  )
}
