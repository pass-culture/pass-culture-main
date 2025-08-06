import cn from 'classnames'
import { useFormContext } from 'react-hook-form'

import { mapDayToFrench } from '@/commons/utils/date'
import { DayCheckbox } from '@/ui-kit/form/DayCheckbox/DayCheckbox'

import { Day, VenueEditionFormValues } from '../types'
import { HourLine } from './HourLine'
import styles from './OpeningHoursForm.module.scss'

export const daysOfWeek: Day[] = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
]

export function OpeningHoursForm() {
  const {
    watch,
    setValue: setFieldValue,
    // setFieldTouched,
  } = useFormContext<VenueEditionFormValues>()

  const days = watch('days')

  return (
    <>
      <fieldset className={styles['inputs-line']}>
        <legend className={styles['legend-days']}>
          Sélectionner vos jours d’ouverture :
        </legend>
        {daysOfWeek.map((day) => {
          const dayLabel = mapDayToFrench(day)
          return (
            <DayCheckbox
              name="days"
              key={day}
              label={dayLabel[0]}
              className={styles['day-checkbox']}
              checked={days.includes(day)}
              tooltipContent={dayLabel}
              onChange={(e) => {
                let newDays = new Set(days)
                if (e.target.checked) {
                  newDays.add(day)
                } else {
                  newDays.delete(day)
                }
                setFieldValue('days', Array.from(newDays))
                if (!e.target.checked) {
                  setFieldValue(`${day}.morningStartingHour`, '')
                  setFieldValue(`${day}.morningEndingHour`, '')
                  setFieldValue(`${day}.afternoonStartingHour`, '')
                  setFieldValue(`${day}.afternoonEndingHour`, '')
                }
              }}
            />
          )
        })}
      </fieldset>
      {days.length > 0 && (
        <table>
          <thead>
            <tr className={styles['row-header']}>
              <th
                scope="col"
                className={cn(
                  styles['column-header'],
                  styles['column-header-first']
                )}
              />
              <th scope="col" className={styles['column-header']}>
                Ouvre à
              </th>
              <th scope="col" className={styles['column-header']}>
                Ferme à
              </th>
            </tr>
          </thead>

          <tbody>
            {days
              .sort((a, b) => daysOfWeek.indexOf(a) - daysOfWeek.indexOf(b))
              .map((day) => (
                <HourLine day={day} key={day} />
              ))}
          </tbody>
        </table>
      )}
    </>
  )
}
