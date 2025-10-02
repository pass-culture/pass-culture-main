import classNames from 'classnames'
import fullError from 'icons/full-error.svg'
import { type ElementType, useId } from 'react'
import { SvgIcon } from 'ui-kit/SvgIcon/SvgIcon'

import { Checkbox, type CheckboxProps } from '../Checkbox/Checkbox'
import styles from './CheckboxGroup.module.scss'

export type CheckboxGroupOption = Omit<CheckboxProps, 'variant'>

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
  /** Display style of the checkbox group, defaults to 'vertical' */
  display?: 'vertical' | 'horizontal'
  /** Variant of the checkboxes (applied to all), defaults to 'default' */
  variant?: 'default' | 'detailed'
  /** If the checkbox group is disabled, making all options unselectable */
  disabled?: boolean
  name: string
  required?: boolean
  asterisk?: boolean
}

export const CheckboxGroup = ({
  label,
  labelTag: LabelTag = 'span',
  description,
  error,
  options,
  display = 'vertical',
  variant = 'default',
  disabled = false,
  name,
  required = false,
  asterisk = true,
}: CheckboxGroupProps) => {
  if (options.length < 2) {
    throw new Error('CheckboxGroup requires at least two options.')
  }

  const labelId = useId()
  const errorId = useId()
  const descriptionId = useId()
  const describedBy = `${error ? errorId : ''} ${description ? descriptionId : ''}`

  return (
    <fieldset
      aria-labelledby={labelId}
      aria-describedby={describedBy}
      className={classNames(
        styles['checkbox-group'],
        styles[`display-${display}`],
        styles[`variant-${variant}`],
        { [styles['disabled']]: disabled }
      )}
    >
      <legend className={styles['checkbox-group-legend']}>
        <LabelTag
          id={labelId}
          className={classNames(styles[`checkbox-group-label-${LabelTag}`], {
            [styles['disabled']]: disabled,
          })}
        >
          {label} {required && asterisk ? ' *' : ''}
        </LabelTag>
      </legend>
      <div className={styles['checkbox-group-header']}>
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
        <div role="alert">
          {error && (
            <div id={errorId}>
              <SvgIcon
                src={fullError}
                alt=""
                width="16"
                className={styles['checkbox-group-error-icon']}
              />
              <span className={styles['checkbox-group-error']}>{error}</span>
            </div>
          )}
        </div>
      </div>
      <div className={styles['checkbox-group-options']}>
        {options.map((option) => {
          return (
            <div className={styles['checkbox-group-item']} key={option.label}>
              {variant === 'default' ? (
                <Checkbox
                  {...option}
                  description={undefined}
                  asset={undefined}
                  collapsed={undefined}
                  hasError={!!error}
                  disabled={disabled || option.disabled}
                  variant="default"
                  name={name}
                />
              ) : (
                <Checkbox
                  {...option}
                  hasError={!!error}
                  disabled={disabled || option.disabled}
                  variant="detailed"
                  name={name}
                />
              )}
            </div>
          )
        })}
      </div>
    </fieldset>
  )
}
