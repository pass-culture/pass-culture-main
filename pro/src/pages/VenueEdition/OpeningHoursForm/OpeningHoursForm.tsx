import { useFormikContext } from 'formik'

import { mapDayToFrench } from 'pages/VenueEdition/OpeningHoursReadOnly/utils'
import { DayCheckbox } from 'screens/IndividualOffer/StocksEventCreation/DayCheckbox'

import { VenueEditionFormValues } from '../types'

import { HourLine } from './HourLine'
import styles from './OpeningHoursForm.module.scss'

const daysOfWeek = [
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
    values: { days },
    setFieldValue,
  } = useFormikContext<VenueEditionFormValues>()

  return (
    <>
      <fieldset className={styles['inputs-line']}>
        <legend className={styles['legend-days']}>
          Sélectionner vos jours d’ouverture :
        </legend>
        {daysOfWeek?.map((engDay) => {
          const frDay = mapDayToFrench(engDay)
          return (
            <DayCheckbox
              letter={frDay[0]}
              label={frDay}
              name="days"
              value={engDay.toLowerCase()}
              className={styles['day-checkbox']}
              key={engDay}
              checked={days.includes(engDay)}
              onClick={async () => {
                await setFieldValue(`${engDay}.morningStartingHour`, '')
                await setFieldValue(`${engDay}.morningEndingHour`, '')
                await setFieldValue(`${engDay}.afternoonStartingHour`, '')
                await setFieldValue(`${engDay}.afternoonEndingHour`, '')
              }}
            />
          )
        })}
      </fieldset>
      {days.length > 0 && (
        <table>
          <thead>
            <tr>
              <th scope="col" className={styles['column-header']}></th>
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
                <HourLine
                  day={
                    // FIX ME: is there a way to avoid this "as" ?
                    day as
                      | 'monday'
                      | 'tuesday'
                      | 'wednesday'
                      | 'thursday'
                      | 'friday'
                      | 'saturday'
                      | 'sunday'
                  }
                  key={day}
                />
              ))}
          </tbody>
        </table>
      )}
    </>
  )
}
