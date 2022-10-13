import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { RadioButton } from '..'
import { FieldSetLayout } from '../shared'

import styles from './RadioGroup.module.scss'

export enum Direction {
  VERTICAL = 'vertical',
  HORIZONTAL = 'horizontal',
}
export interface IRadioGroupProps {
  direction?: Direction.HORIZONTAL | Direction.VERTICAL
  disabled?: boolean
  hideFooter?: boolean
  name: string
  legend?: string
  group: {
    label: string
    value: string
  }[]
  className?: string
  withBorder?: boolean
}

const RadioGroup = ({
  direction = Direction.VERTICAL,
  disabled,
  hideFooter = false,
  group,
  name,
  legend,
  className,
  withBorder,
}: IRadioGroupProps): JSX.Element => {
  const [, meta] = useField({ name })

  return (
    <FieldSetLayout
      className={cn(
        styles['radio-group'],
        styles[`radio-group-${direction}`],
        className
      )}
      dataTestId={`wrapper-${name}`}
      error={meta.touched && !!meta.error ? meta.error : undefined}
      hideFooter={hideFooter}
      legend={legend}
      name={`radio-group-${name}`}
    >
      {group.map(item => (
        <div className={styles['radio-group-item']} key={item.label}>
          <RadioButton
            disabled={disabled}
            label={item.label}
            name={name}
            value={item.value}
            withBorder={withBorder}
            hasError={meta.touched && !!meta.error}
          />
        </div>
      ))}
    </FieldSetLayout>
  )
}

export default RadioGroup
