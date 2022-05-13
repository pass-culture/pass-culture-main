import CheckboxGroupItem from './CheckboxGroupItem'
import { FieldSetLayout } from '../shared'
import React from 'react'
import cn from 'classnames'
import styles from './CheckboxGroup.module.scss'
import { useField } from 'formik'

interface ICheckboxGroupProps {
  groupName: string
  legend: string
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
  legend,
  className,
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
    </FieldSetLayout>
  )
}

export default CheckboxGroup
