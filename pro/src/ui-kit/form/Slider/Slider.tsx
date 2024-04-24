import { useField } from 'formik'
import React from 'react'

import styles from './Slider.module.scss'

const DEFAULT_SLIDER_MIN_VALUE = 0
const DEFAULT_SLIDER_MAX_VALUE = 100
const DEFAULT_SLIDER_STEP_VALUE = 1
export interface SliderProps extends React.HTMLProps<HTMLInputElement> {
  fieldName: string
  scale?: string
  hideLabel?: boolean
  displayMinMaxValues?: boolean
  displayValue?: boolean
}

export const Slider = ({
  fieldName,
  scale = '',
  hideLabel = false,
  displayMinMaxValues = true,
  displayValue = false,
  ...inputAttrs
}: SliderProps): JSX.Element => {
  const [field] = useField(fieldName)

  const min = inputAttrs.min || DEFAULT_SLIDER_MIN_VALUE
  const max = inputAttrs.max || DEFAULT_SLIDER_MAX_VALUE

  return (
    <div>
      <div className={styles['slider-header']}>
        <label
          htmlFor={fieldName}
          className={hideLabel ? 'visually-hidden' : ''}
        >
          {inputAttrs.label}
        </label>
        {displayValue && (
          <span className={styles['input-value']}>
            {field.value}&nbsp;{scale}
          </span>
        )}
      </div>
      <input
        {...field}
        type="range"
        className={styles.slider}
        min={min}
        max={max}
        step={inputAttrs.step || DEFAULT_SLIDER_STEP_VALUE}
      />
      {displayMinMaxValues && (
        <div className={styles['min-max-container']}>
          <span>
            <span className="visually-hidden">Entre </span>
            {`${min} ${scale}`}
          </span>
          <span>
            <span className="visually-hidden">et </span>
            {`${max} ${scale}`}
          </span>
        </div>
      )}
    </div>
  )
}
