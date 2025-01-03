import classNames from 'classnames'
import { useField } from 'formik'

import { CheckboxVariant } from '../shared/BaseCheckbox/BaseCheckbox'
import { FieldSetLayout } from '../shared/FieldSetLayout/FieldSetLayout'

import styles from './CheckboxGroup.module.scss'
import { CheckboxGroupItem } from './CheckboxGroupItem'

interface CheckboxGroupProps {
  groupName: string
  legend: string
  group: {
    name: string
    label: string
    description?: string
    icon?: string
    onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
  }[]
  disabled?: boolean
  isOptional?: boolean
  variant?: CheckboxVariant
  inline?: boolean
}

export const CheckboxGroup = ({
  group,
  groupName,
  legend,
  disabled,
  isOptional,
  variant,
  inline = false,
}: CheckboxGroupProps): JSX.Element => {
  const [, meta, helpers] = useField({ name: groupName })
  const hasError = meta.touched && !!meta.error

  return (
    <FieldSetLayout
      error={hasError ? meta.error : undefined}
      legend={legend}
      name={groupName}
      isOptional={isOptional}
    >
      <div
        className={classNames(styles['checkbox-group'], {
          [styles['inline']]: inline,
        })}
      >
        {group.map((item) => (
          <div className={styles['checkbox-group-item']} key={item.name}>
            <CheckboxGroupItem
              icon={item.icon}
              hasError={hasError}
              label={item.label}
              name={item.name}
              setGroupTouched={() =>
                !meta.touched ? helpers.setTouched(true) : null
              }
              disabled={disabled}
              onChange={item.onChange}
              {...(hasError ? { ariaDescribedBy: `error-${groupName}` } : {})}
              variant={variant}
            />
          </div>
        ))}
      </div>
    </FieldSetLayout>
  )
}
