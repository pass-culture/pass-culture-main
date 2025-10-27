import { useId } from 'react'

import { FieldFooter } from '@/design-system/common/FieldFooter/FieldFooter'
import type { RequiredIndicator } from '@/design-system/common/types'
import { IconRadio } from '@/ui-kit/form/IconRadio/IconRadio'

import styles from './IconRadioGroup.module.scss'

export type IconRadioGroupValues = {
  /** Hidden label for the radio button shown as a tooltip on hover/focus */
  label: string
  /** Icon element displayed in the small round radio button */
  icon: string | JSX.Element
  /** Value of the radio button */
  value: string
}

export interface IconRadioGroupProps {
  name: string
  legend: string
  group: IconRadioGroupValues[]
  /** What type of required indicator is displayed */
  requiredIndicator?: RequiredIndicator
  error?: string
  required?: boolean
  value: string
  onChange: (value: string) => void
}

export const IconRadioGroup = ({
  group,
  name,
  legend,
  required = false,
  requiredIndicator = 'symbol',
  error,
  value,
  onChange,
}: IconRadioGroupProps): JSX.Element => {
  const scaleId = useId()
  const errorId = useId()

  const hasError = Boolean(error)
  const scale =
    group.length > 0 ? [group[0].label, group[group.length - 1].label] : []

  const displayScale = scale.length > 1

  return (
    <fieldset
      className={styles['icon-radio-group']}
      name={`icon-radio-group-${name}`}
      aria-describedby={`${hasError ? errorId : ''} ${scaleId}`}
    >
      <legend className={styles['icon-radio-group-legend']}>
        {legend}
        {required && requiredIndicator === 'symbol' && <>&nbsp;*</>}
      </legend>
      {displayScale && (
        <p className={styles['visually-hidden']} id={scaleId}>
          L’échelle de sélection va de {scale[0]} à {scale[1]}
        </p>
      )}
      <div className={styles['icon-radio-group-items-container']}>
        <div className={styles['icon-radio-group-items']}>
          {group.map((item) => (
            <IconRadio
              name={name}
              className={styles['icon-radio-group-item']}
              key={item.label}
              icon={item.icon}
              label={item.label}
              checked={item.value === value}
              hasError={hasError}
              onChange={() => {
                onChange(item.value)
              }}
            />
          ))}
        </div>
        {displayScale && (
          <div className={styles['icon-radio-group-scale']} aria-hidden="true">
            {scale.map((s) => (
              <span key={s}>{s}</span>
            ))}
          </div>
        )}
        <FieldFooter error={error} errorId={errorId} />
      </div>
    </fieldset>
  )
}
