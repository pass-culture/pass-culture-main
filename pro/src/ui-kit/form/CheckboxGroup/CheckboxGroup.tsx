import classNames from 'classnames'
import { useId } from 'react'

import { Checkbox, type CheckboxProps } from '@/design-system/Checkbox/Checkbox'
import { FieldError } from '@/ui-kit/form/shared/FieldError/FieldError'

import styles from './CheckboxGroup.module.scss'

type GroupOption = {
  label: string
  icon?: string
  collapsed?: JSX.Element
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
  onBlur?: (event: React.ChangeEvent<HTMLInputElement>) => void
  checked?: boolean
  indeterminate?: boolean
  ref?: React.RefObject<HTMLInputElement>
  sizing?: CheckboxProps['sizing']
}

export type CheckboxGroupProps = {
  legend: string | React.ReactNode
  group: GroupOption[]
  disabled?: boolean
  required?: boolean
  variant?: CheckboxProps['variant']
  inline?: boolean
  asterisk?: boolean
  error?: string
  name?: string
  /**
   * Callback function to handle changes in the radio group.
   */
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void
}

export const CheckboxGroup = ({
  group,
  legend,
  disabled,
  required,
  inline = false,
  asterisk = true,
  error,
  name,
  onChange,
}: CheckboxGroupProps): JSX.Element => {
  const errorId = useId()

  return (
    <fieldset aria-describedby={errorId}>
      {legend && (
        <legend className={styles['legend']}>
          {legend}
          {required && asterisk ? ' *' : ''}
        </legend>
      )}
      <div
        className={classNames(styles['checkbox-group'], {
          [styles['inline']]: inline,
        })}
      >
        {group.map((item) => (
          <div className={styles['checkbox-group-item']} key={item.label}>
            <Checkbox
              asset={
                item.icon ? { variant: 'icon', src: item.icon } : undefined
              }
              hasError={Boolean(error)}
              label={item.label}
              disabled={disabled}
              onChange={(ev) => {
                item.onChange?.(ev)
                onChange?.(ev)
              }}
              onBlur={item.onBlur}
              variant="detailed"
              checked={Boolean(item.checked)}
              collapsed={item.collapsed}
              indeterminate={item.indeterminate}
              name={name}
              ref={item.ref}
              sizing={item.sizing}
            />
          </div>
        ))}
      </div>
      <div role="alert" id={errorId}>
        {error && <FieldError className={styles['error']}>{error}</FieldError>}
      </div>
    </fieldset>
  )
}
