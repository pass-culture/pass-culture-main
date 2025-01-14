import cn from 'classnames'
import { useId } from 'react'

import { isValidTime } from 'commons/utils/timezone'

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

  const { interval = 15, min = '00:00', max = '23:59' } = suggestedTimeList
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

  // When registered, time value might be translated to '9:00'.
  // This is a workaround to init and display the value as '09:00'.
  const paddedValue =
    props.value && props.value.length === 4 ? `0${props.value}` : props.value
  const formattedValue = isValidTime(paddedValue) ? paddedValue : ''

  return (
    <>
      <BaseInput
        type="time"
        {...(hasTimeOptions ? { list: optionsListId } : {})}
        autoComplete="off"
        {...props}
        value={formattedValue}
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
