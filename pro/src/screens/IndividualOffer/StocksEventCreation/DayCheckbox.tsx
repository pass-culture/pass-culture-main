import { useField } from 'formik'
import React from 'react'

import { BaseCheckbox } from 'ui-kit/form/shared'

import styles from './DayCheckbox.module.scss'

type DayCheckboxProps = React.InputHTMLAttributes<HTMLInputElement> & {
  label: string
  letter: string
  name: string
}

export const DayCheckbox = ({
  label,
  letter,
  ...inputProps
}: DayCheckboxProps): JSX.Element => {
  const [field] = useField(inputProps.name)

  return (
    <BaseCheckbox
      label={undefined}
      {...field}
      {...inputProps}
      className={styles['checkbox']}
      aria-label={label}
      data-letter={letter}
    />
  )
}
