import cn from 'classnames'
import { useField } from 'formik'
import React from 'react'

import { FieldError } from '../shared'

import styles from './CheckboxGroup.module.scss'
import CheckboxGroupItem from './CheckboxGroupItem'

interface ICheckboxGroupProps {
  groupName: string
  group: {
    name: string
    label: string
    icon?: React.FunctionComponent<React.SVGProps<SVGSVGElement>>
  }[]
  className?: string
}

const CheckboxGroup = ({
  group,
  groupName,
  className,
}: ICheckboxGroupProps): JSX.Element => {
  const [, meta, helpers] = useField({ name: groupName })

  return (
    <div
      className={cn(
        styles['checkbox-group'],
        {
          [styles['has-error']]: meta.touched && !!meta.error,
        },
        className
      )}
    >
      {group.map(item => (
        <div className={styles['checkbox-group-item']} key={item.name}>
          <CheckboxGroupItem
            Icon={item.icon}
            hasError={meta.touched && !!meta.error}
            label={item.label}
            name={item.name}
            setGroupTouched={() =>
              !meta.touched ? helpers.setTouched(true) : null
            }
          />
        </div>
      ))}
      <div className={styles['checkbox-group-error-wrapper']}>
        {meta.touched && !!meta.error && <FieldError>{meta.error}</FieldError>}
      </div>
    </div>
  )
}

export default CheckboxGroup
