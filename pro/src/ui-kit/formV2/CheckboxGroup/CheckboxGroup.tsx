import classNames from 'classnames'
import { useId } from 'react'

import { RequireAtLeastOne } from 'ui-kit/form/RadioGroup/RadioGroup'
import { CheckboxVariant } from 'ui-kit/form/shared/BaseCheckbox/BaseCheckbox'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'

import { Checkbox } from '../Checkbox/Checkbox'

import styles from './CheckboxGroup.module.scss'

type GroupOption = {
  name: string
  label: string | React.ReactNode
  icon?: string
  childrenOnChecked?: JSX.Element
  onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
  onBlur?: (event: React.ChangeEvent<HTMLInputElement>) => void
  checked?: boolean
}

export type CheckboxGroupProps = RequireAtLeastOne<
  {
    name: string
    legend?: string | React.ReactNode
    describedBy?: string
    group: GroupOption[]
    disabled?: boolean
    required?: boolean
    variant?: CheckboxVariant
    inline?: boolean
    asterisk?: boolean
    error?: string
  },
  'legend' | 'describedBy'
>

export const CheckboxGroup = ({
  group,
  name,
  legend,
  describedBy,
  disabled,
  required,
  variant,
  inline = false,
  asterisk = true,
  error,
}: CheckboxGroupProps): JSX.Element => {
  const errorId = useId()

  return (
    <fieldset aria-describedby={`${describedBy || ''} ${errorId}`}>
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
          <div className={styles['checkbox-group-item']} key={item.name}>
            <Checkbox
              icon={item.icon}
              error={error}
              displayErrorMessage={false}
              label={item.label}
              name={item.name}
              disabled={disabled}
              onChange={item.onChange}
              onBlur={item.onBlur}
              variant={variant}
              checked={item.checked}
              childrenOnChecked={item.childrenOnChecked}
            />
          </div>
        ))}
      </div>
      <div role="alert" id={errorId}>
        {error && (
          <FieldError name={name} className={styles['error']}>
            {error}
          </FieldError>
        )}
      </div>
    </fieldset>
  )
}
