import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import FieldError from '../FieldError'

import styles from './CheckboxGroup.module.scss'
import CheckboxGroupItem from './CheckboxGroupItem'

interface ICheckboxGroupProps {
  name: string
  group: {
    value: string
    label: string
  }[]
  className?: string
}

const CheckboxGroup = ({
  name,
  group,
  className,
}: ICheckboxGroupProps): JSX.Element => {
  const [field, meta, helpers] = useField({ name })

  return (
    <div className={cn(styles['checkbox-group'], className)}>
      {group.map(item => (
        <div className={styles['checkbox-group-item']} key={item.value}>
          <CheckboxGroupItem
            formikFieldValue={field.value}
            label={item.label}
            setValue={helpers.setValue}
            value={item.value}
          />
        </div>
      ))}

      {meta.touched && !!meta.error && <FieldError>{meta.error}</FieldError>}
    </div>
  )
}

export default CheckboxGroup
