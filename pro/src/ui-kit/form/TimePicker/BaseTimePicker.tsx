import cn from 'classnames'
import React, { useId } from 'react'

import { BaseInput, BaseInputProps } from '../shared/BaseInput/BaseInput'

import styles from './BaseTimePicker.module.scss'
import { SuggestedTimeList } from './types'

type Props = Omit<BaseInputProps, 'value'> & {
  value: string
  suggestedTimeList?: SuggestedTimeList
}

const getTimeOptions = (suggestedTimeList?: SuggestedTimeList) => {
  if (!suggestedTimeList || !Object.keys(suggestedTimeList).length) {
    return []
  }

  const { interval = 1, min = '00:00', max = '23:59' } = suggestedTimeList
  const [minHours, minMinutes] = min.split(':').map(Number)
  const [maxHours, maxMinutes] = max.split(':').map(Number)

  const timeOptions = []
  for (let hours = minHours; hours <= maxHours; hours++) {
    for (let minutes = 0; minutes < 60; minutes += interval) {
      if (hours === minHours && minutes < minMinutes) {
        continue
      }
      if (hours === maxHours && minutes > maxMinutes) {
        break
      }
      timeOptions.push(
        `${hours.toString().padStart(2, '0')}:${minutes
          .toString()
          .padStart(2, '0')}`
      )
    }
  }

  return timeOptions
}

export const BaseTimePicker = ({
  className,
  suggestedTimeList = { interval: 15 },
  ...props
}: Props): JSX.Element => {
  const optionsListId = useId()
  const timeOptions = getTimeOptions(suggestedTimeList)
  const hasTimeOptions = timeOptions.length > 0

  return (
    <>
      <BaseInput
        type="time"
        {...(hasTimeOptions ? { list: optionsListId } : {})}
        placeholder="HH:MM"
        autoComplete="off"
        {...props}
        className={cn(className, styles['timepicker'])}
      />
      {hasTimeOptions && (
        <datalist id={optionsListId} data-testid="timepicker-datalist">
          {timeOptions.map((time) => (
            <option key={time} value={time}>
              {time}
            </option>
          ))}
        </datalist>
      )}
    </>
  )
}
