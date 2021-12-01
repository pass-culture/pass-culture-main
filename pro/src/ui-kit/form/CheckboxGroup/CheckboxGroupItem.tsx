import React from 'react'

import styles from './CheckboxGroup.module.scss'

interface ICheckboxProps {
  value: string
  label: string
  formikFieldValue: string[]
  setValue(value: string[]): void
}

const CheckboxGroupItem = ({
  value,
  label,
  formikFieldValue,
  setValue,
}: ICheckboxProps): JSX.Element => {
  const handleChange = () => {
    const values = formikFieldValue || []
    const index = values.indexOf(value)

    if (index === -1) {
      values.push(value)
    } else {
      values.splice(index, 1)
    }

    setValue(values)
  }

  return (
    <label className={styles['checkbox-label']} key={value}>
      <input
        checked={formikFieldValue.includes(value)}
        className={styles['checkbox-input']}
        onChange={handleChange}
        type="checkbox"
        value={value}
      />

      {label}
    </label>
  )
}

export default CheckboxGroupItem
