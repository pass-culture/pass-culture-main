import cn from 'classnames'
import React, { useId } from 'react'

import { BaseInput, BaseInputProps } from '../shared/BaseInput/BaseInput'

import styles from './BaseTimePicker.module.scss'

type Props = Omit<BaseInputProps, 'value'> & {
  value: string
  showIntervalList?: boolean
}

const TIME_OPTIONS = Array.from({ length: 24 * 4 }, (_, i) => {
  const hours = Math.floor(i / 4)
  const minutes = (i % 4) * 15
  return `${hours.toString().padStart(2, '0')}:${minutes
    .toString()
    .padStart(2, '0')}`
})

export const BaseTimePicker = ({
  className,
  showIntervalList = true,
  ...props
}: Props): JSX.Element => {
  const optionsListId = useId()

  return (
    <>
      <BaseInput
        type="time"
        {...(showIntervalList ? { list: optionsListId } : {})}
        placeholder="HH:MM"
        autoComplete="off"
        {...props}
        className={cn(className, styles['timepicker'])}
      />
      {showIntervalList && (
        <datalist id={optionsListId}>
          {TIME_OPTIONS.map((time) => (
            <option key={time} value={time}>
              {time}
            </option>
          ))}
        </datalist>
      )}
    </>
  )
}
