import { useField } from 'formik'
import { useId } from 'react'

import { IconRadio } from 'ui-kit/form/IconRadioGroup/IconRadio/IconRadio'

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
  isOptional?: boolean
  hideAsterisk?: boolean
}

export const IconRadioGroup = ({
  group,
  name,
  legend,
  isOptional = false,
  hideAsterisk,
}: IconRadioGroupProps): JSX.Element => {
  const [, meta] = useField({ name })

  const scaleId = useId()

  const hasError = meta.touched && !!meta.error
  const scale =
    group.length > 0 ? [group[0].label, group[group.length - 1].label] : []

  const displayScale = scale.length > 1

  return (
    <>
      <FieldSetLayout
        className={styles['icon-radio-group']}
        error={hasError ? meta.error : undefined}
        legend={legend}
        name={`icon-radio-group-${name}`}
        hideFooter
        isOptional={isOptional}
        hideAsterisk={hideAsterisk}
        ariaDescribedBy={displayScale ? scaleId : undefined}
      >
        {displayScale && (
          <p className={styles['visually-hidden']} id={scaleId}>
            L’échelle de sélection va de {scale[0]} à {scale[1]}
          </p>
        )}
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
          {displayScale && (
            <div
              className={styles['icon-radio-group-scale']}
              aria-hidden="true"
            >
              {scale.map((s) => (
                <span key={s}>{s}</span>
              ))}
            </div>
          )}
        </div>
      </FieldSetLayout>
    </>
  )
}
