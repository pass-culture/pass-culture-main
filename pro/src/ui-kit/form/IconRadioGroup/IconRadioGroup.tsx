import { useField } from 'formik'

import { IconRadio } from 'ui-kit/form/IconRadioGroup/IconRadio/IconRadio'
import { FieldError } from 'ui-kit/form/shared/FieldError/FieldError'

import { FieldSetLayout } from '../shared/FieldSetLayout/FieldSetLayout'

import styles from './IconRadioGroup.module.scss'

export type IconRadioGroupValues = {
  label: string
  icon: string | JSX.Element
  value: string
}

interface IconRadioGroupProps {
  name: string
  legend?: string
  /**
   * ```
   * {
   *   label: Hidden label for the radio button shown as a tooltip on hover/focus
   *   icon: Icon element displayed in the small round radio button
   *   value: Value of the radio button
   * }
   * ```
   */
  group: IconRadioGroupValues[]
  children?: React.ReactNode
}

export const IconRadioGroup = ({
  group,
  name,
  legend,
  children,
}: IconRadioGroupProps): JSX.Element => {
  const [, meta] = useField({ name })
  const hasError = meta.touched && !!meta.error

  return (
    <>
      <FieldSetLayout
        className={styles['icon-radio-group']}
        error={hasError ? meta.error : undefined}
        legend={legend}
        name={`icon-radio-group-${name}`}
        hideFooter={true}
      >
        <div className={styles['icon-radio-group-items']}>
          {group.map((item) => (
            <IconRadio
              name={name}
              className={styles['icon-radio-group-item']}
              key={item.label}
              icon={item.icon}
              label={item.label}
              value={item.value}
              hasError={hasError}
              {...(hasError ? { 'aria-describedby': `error-${name}` } : {})}
            />
          ))}
          <div className={styles['icon-radio-group-scale']}>{children}</div>
        </div>
        <div className={styles['fieldset-layout-error']}>
          {!!meta.error && (
            <FieldError name={`icon-radio-group-${name}`}>
              {meta.error}
            </FieldError>
          )}
        </div>
      </FieldSetLayout>
    </>
  )
}
