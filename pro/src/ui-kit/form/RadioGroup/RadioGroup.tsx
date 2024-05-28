import cn from 'classnames'
import { useField } from 'formik'

import { RadioButton } from '../RadioButton/RadioButton'
import { FieldSetLayout } from '../shared/FieldSetLayout/FieldSetLayout'

import styles from './RadioGroup.module.scss'

export enum Direction {
  VERTICAL = 'vertical',
  HORIZONTAL = 'horizontal',
}
interface RadioGroupProps {
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

export const RadioGroup = ({
  direction = Direction.VERTICAL,
  disabled,
  hideFooter = false,
  group,
  name,
  legend,
  className,
  withBorder,
}: RadioGroupProps): JSX.Element => {
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
      isOptional // There should always be an element selected in a radio group, thus it doesn't need to be marked as required
    >
      {group.map((item) => (
        <div className={styles['radio-group-item']} key={item.label}>
          <RadioButton
            disabled={disabled}
            label={item.label}
            name={name}
            value={item.value}
            withBorder={withBorder}
            hasError={meta.touched && !!meta.error}
            fullWidth
          />
        </div>
      ))}
    </FieldSetLayout>
  )
}
