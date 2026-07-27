import { useFormContext } from 'react-hook-form'

import { getPublicationHoursOptions } from '@/commons/utils/date'
import { DatePicker } from '@/ui-kit/form/DatePicker/DatePicker'
import { Select } from '@/ui-kit/form/Select/Select'

import styles from './DateAndTimePicker.module.scss'

type DateAndTimePickerProps = {
  dateName: string
  timeName: string
  disabled?: boolean
  minDate?: Date
}

export const DateAndTimePicker = ({
  dateName,
  timeName,
  disabled = false,
  minDate = new Date(),
}: DateAndTimePickerProps) => {
  const { register, formState, trigger } = useFormContext()
  const publicationHoursOptions = getPublicationHoursOptions()

  const dateError = formState.errors[dateName]?.message as string | undefined
  const timeError = formState.errors[timeName]?.message as string | undefined

  return (
    <div className={styles['inputs-row']}>
      <DatePicker
        label="Date"
        minDate={minDate}
        className={styles['date-picker']}
        disabled={disabled}
        required
        {...register(dateName, {
          onBlur: () => trigger(timeName),
        })}
        error={dateError}
      />
      <Select
        label="Heure"
        options={publicationHoursOptions}
        defaultOption={{ label: 'HH:MM', value: '' }}
        className={styles['time-picker']}
        disabled={disabled}
        required
        {...register(timeName)}
        error={timeError}
      />
    </div>
  )
}
