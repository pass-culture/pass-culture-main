import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { RadioButton } from '..'
import { FieldSetLayout } from '../shared'

import styles from './RadioGroup.module.scss'

interface IRadioGroupProps {
  name: string
  legend: string
  group: {
    label: string
    value: string
  }[]
  className?: string
}

const RadioGroup = ({
  group,
  name,
  legend,
  className,
}: IRadioGroupProps): JSX.Element => {
  const [, meta] = useField({ name })

  return (
    <FieldSetLayout
      className={cn(styles['radio-group'], className)}
      error={meta.touched && !!meta.error ? meta.error : undefined}
      hideFooter
      legend={legend}
      name={`radio-group-${name}`}
    >
      {group.map(item => (
        <div className={styles['radio-group-item']} key={item.label}>
          <RadioButton label={item.label} name={name} value={item.value} />
        </div>
      ))}
    </FieldSetLayout>
  )
}

export default RadioGroup
