import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { FieldSetLayout } from '../shared'

import styles from './CheckboxGroup.module.scss'
import CheckboxGroupItem from './CheckboxGroupItem'

export interface ICheckboxGroupProps {
  groupName: string
  legend: string
  group: {
    name: string
    label: string
    description?: string
    icon?: string
    onChange?: (event: React.ChangeEvent<HTMLInputElement>) => void
  }[]
  className?: string
  disabled?: boolean
}

const CheckboxGroup = ({
  group,
  groupName,
  legend,
  className,
  disabled,
}: ICheckboxGroupProps): JSX.Element => {
  const [, meta, helpers] = useField({ name: groupName })

  return (
    <FieldSetLayout
      className={cn(styles['checkbox-group'], className)}
      error={meta.touched && !!meta.error ? meta.error : undefined}
      legend={legend}
      name={groupName}
    >
      {group.map(item => (
        <div className={styles['checkbox-group-item']} key={item.name}>
          <CheckboxGroupItem
            icon={item.icon}
            hasError={meta.touched && !!meta.error}
            label={item.label}
            description={item.description}
            name={item.name}
            setGroupTouched={() =>
              !meta.touched ? helpers.setTouched(true) : null
            }
            disabled={disabled}
            onChange={item.onChange}
          />
        </div>
      ))}
    </FieldSetLayout>
  )
}

export default CheckboxGroup
