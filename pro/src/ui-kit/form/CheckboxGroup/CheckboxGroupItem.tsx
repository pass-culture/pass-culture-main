import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import styles from './CheckboxGroup.module.scss'

interface ICheckboxProps {
  setGroupTouched(): void
  name: string
  label: string
  Icon?: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
}

const CheckboxGroupItem = ({
  setGroupTouched,
  label,
  name,
  Icon,
}: ICheckboxProps): JSX.Element => {
  const [field] = useField({ name, type: 'checkbox' })

  const onChange = (event: React.ChangeEvent<HTMLInputElement>): void => {
    setGroupTouched()
    field.onChange(event)
  }

  return (
    <label className={cn(styles['checkbox-label'])}>
      <input
        className={styles['checkbox-input']}
        type="checkbox"
        {...field}
        onChange={onChange}
      />
      {!!Icon && <Icon className={styles['checkbox-icon']} />}

      {label}
    </label>
  )
}

export default CheckboxGroupItem
