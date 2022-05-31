import { FieldSetLayout } from '../shared'
import { RadioButton } from '..'
import React from 'react'
import cn from 'classnames'
import styles from './RadioGroup.module.scss'
import { useField } from 'formik'

interface IRadioGroupProps {
  name: string
  legend?: string
  group: {
    label: string
    value: string
  }[]
  className?: string
  radiosWithBorder?: boolean
}

const RadioGroup = ({
  group,
  name,
  legend,
  className,
  radiosWithBorder,
}: IRadioGroupProps): JSX.Element => {
  const [, meta] = useField({ name })

  return (
    <FieldSetLayout
      className={cn(styles['radio-group'], className)}
      dataTestId={`wrapper-${name}`}
      error={meta.touched && !!meta.error ? meta.error : undefined}
      hideFooter
      legend={legend}
      name={`radio-group-${name}`}
    >
      {group.map(item => (
        <div className={styles['radio-group-item']} key={item.label}>
          <RadioButton
            label={item.label}
            name={name}
            value={item.value}
            withBorder={radiosWithBorder}
          />
        </div>
      ))}
    </FieldSetLayout>
  )
}

export default RadioGroup
