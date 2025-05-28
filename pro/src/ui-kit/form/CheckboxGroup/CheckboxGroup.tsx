import classNames from 'classnames'
import { useField } from 'formik'

import { FieldSetLayout } from '../shared/FieldSetLayout/FieldSetLayout'

import styles from './CheckboxGroup.module.scss'
import { CheckboxGroupItem } from './CheckboxGroupItem'

type CheckboxGroupProps = {
  groupName: string
  legend: string | React.ReactNode
  describedBy?: string
  group: {
    name: string
    label: string
    icon?: string
    onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
    collapsed?: JSX.Element
  }[]
  disabled?: boolean
  isOptional?: boolean
  inline?: boolean
  hideAsterisk?: boolean
}

export const CheckboxGroup = ({
  group,
  groupName,
  legend,
  describedBy,
  disabled,
  isOptional,
  inline = false,
  hideAsterisk,
}: CheckboxGroupProps): JSX.Element => {
  const [, meta, helpers] = useField({ name: groupName })
  const hasError = meta.touched && !!meta.error

  return (
    <FieldSetLayout
      error={hasError ? meta.error : undefined}
      legend={legend}
      name={groupName}
      ariaDescribedBy={describedBy}
      isOptional={isOptional}
      hideFooter
      hideAsterisk={hideAsterisk}
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
              collapsed={item.collapsed}
            />
          </div>
        ))}
      </div>
    </FieldSetLayout>
  )
}
