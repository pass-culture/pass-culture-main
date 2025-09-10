import classNames from 'classnames'
import fullError from 'icons/full-error.svg'
import { type ElementType, useId } from 'react'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { Checkbox, type CheckboxProps } from '../Checkbox/Checkbox'
import styles from './CheckboxGroup.module.scss'

type CheckboxGroupOptionSimple = Omit<
  CheckboxProps,
  'checked' | 'onChange' | 'hasError' | 'disabled' | 'variant' | 'asset'
> & {
  label: string
  value: string
  variant?: 'default'
  asset?: never
}

type CheckboxGroupOptionDetailed = Omit<
  CheckboxProps,
  'checked' | 'onChange' | 'hasError' | 'disabled' | 'variant'
> & {
  label: string
  value: string
  variant: 'detailed'
  asset?: CheckboxProps['asset']
}

export type CheckboxGroupOption =
  | CheckboxGroupOptionSimple
  | CheckboxGroupOptionDetailed

type CheckboxGroupProps = {
  /** Label for the checkbox group */
  label: string
  /** Tag for the label, defaults to 'span', can be 'h1', 'h2', etc. */
  labelTag?: ElementType
  /** Description for the checkbox group */
  description?: string
  /** Error message for the checkbox group */
  error?: string
  /** List of options as checkboxes */
  options: CheckboxGroupOption[]
  /** Controlled selected values */
  value: string[]
  /** Event handler called with the new array of selected values */
  onChange: (value: string[]) => void
  /** Display style of the checkbox group, defaults to 'vertical' */
  display?: 'vertical' | 'horizontal'
  /** Variant of the checkboxes (applied to all), defaults to 'default' */
  variant?: 'default' | 'detailed'
  /** If the checkbox group is disabled, making all options unselectable */
  disabled?: boolean
}

export const CheckboxGroup = ({
  label,
  labelTag: LabelTag = 'span',
  description,
  error,
  options,
  value,
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

  const selectedValues = value ?? []

  const handleChange = (option: CheckboxGroupOption) => {
    let newValues: string[]
    if (selectedValues.includes(option.value)) {
      newValues = selectedValues.filter((v) => v !== option.value)
    } else {
      newValues = [...selectedValues, option.value]
    }
    onChange?.(newValues)
  }

  return (
    <div
      role="group"
      aria-labelledby={labelId}
      aria-describedby={describedBy}
      className={classNames(
        styles['checkbox-group'],
        styles[`display-${display}`],
        styles[`variant-${variant}`],
        { [styles['disabled']]: disabled }
      )}
    >
      <div className={styles['checkbox-group-header']}>
        <LabelTag
          id={labelId}
          className={classNames(styles[`checkbox-group-label-${LabelTag}`], {
            [styles['disabled']]: disabled,
          })}
        >
          {label}
        </LabelTag>
        {description && (
          <span
            id={descriptionId}
            className={classNames(styles['checkbox-group-description'], {
              [styles['disabled']]: disabled,
              [styles[`has-label-${LabelTag}`]]: LabelTag,
            })}
          >
            {description}
          </span>
        )}
        <div role="alert" id={errorId}>
          {error && (
            <>
              <SvgIcon
                src={fullError}
                alt=""
                width="16"
                className={styles['checkbox-group-error-icon']}
              />
              <span className={styles['checkbox-group-error']}>{error}</span>
            </>
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
                  asset: option.asset,
                  collapsed: option.collapsed,
                }
              : {}

          return (
            <Checkbox
              key={option.value}
              label={option.label}
              checked={checked}
              onChange={() => handleChange(option)}
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
