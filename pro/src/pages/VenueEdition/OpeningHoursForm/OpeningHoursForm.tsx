import { useFormikContext } from 'formik'

import { mapDayToFrench } from 'pages/VenueEdition/OpeningHoursReadOnly/utils'
import { DayCheckbox } from 'screens/IndividualOffer/StocksEventCreation/DayCheckbox'

import { VenueEditionFormValues } from '../types'

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
  } = useFormikContext<VenueEditionFormValues>()

  return (
    <>
      <fieldset className={styles['day-inputs']}>
        <legend className={styles['legend']}>
          Sélectionner vos jours d’ouverture :
        </legend>
        {daysOfWeek.map((engDay) => {
          const frDay = mapDayToFrench(engDay)
          return (
            <DayCheckbox
              letter={frDay[0]}
              label={frDay}
              name="days"
              value={engDay.toLowerCase()}
              className={styles['day-checkbox']}
              key={engDay}
            />
          )
        })}
      </fieldset>
      {days.length > 0 && (
        <ul>
          {days
            .sort((a, b) => daysOfWeek.indexOf(a) - daysOfWeek.indexOf(b))
            .map((day) => (
              <li key={day}>{mapDayToFrench(day)}</li>
            ))}
        </ul>
      )}
    </>
  )
}
