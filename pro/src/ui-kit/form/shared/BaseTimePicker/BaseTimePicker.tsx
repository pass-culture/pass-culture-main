import cn from 'classnames'
import { ForwardedRef, forwardRef, useId } from 'react'

import { isValidTime } from '@/commons/utils/timezone'

import { BaseInput, BaseInputProps } from '../BaseInput/BaseInput'
import styles from './BaseTimePicker.module.scss'

export type SuggestedTimeList = {
  interval?: number
  min?: string
  max?: string
}

type Props = Omit<BaseInputProps, 'value'> & {
  value?: string
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

export const BaseTimePicker = forwardRef(
  (
    { className, suggestedTimeList = { interval: 15 }, ...props }: Props,
    ref: ForwardedRef<HTMLInputElement>
  ): JSX.Element => {
    const optionsListId = useId()
    const timeOptions = getTimeOptions(suggestedTimeList)
    const hasTimeOptions = timeOptions.length > 0

    // When registered, time value might be translated to '9:00'.
    // This is a workaround to init and display the value as '09:00'.
    if (props.value?.length === 4) {
      props.value = `0${props.value}`
    }

    return (
      <>
        <BaseInput
          type="time"
          {...(hasTimeOptions ? { list: optionsListId } : {})}
          autoComplete="off"
          {...props}
          //  If the component has no ref, it is controlled, and the value must not be undefined
          //  Otherwise React thinks it becomes controlled, and switching inbetween control modes is forbidden
          value={
            ref ? props.value : isValidTime(props.value) ? props.value : ''
          }
          className={cn(className, styles['timepicker'])}
          ref={ref}
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
)

BaseTimePicker.displayName = 'BaseTimePicker'
