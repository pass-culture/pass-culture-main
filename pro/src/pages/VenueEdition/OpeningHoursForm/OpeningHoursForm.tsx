import { useFormikContext } from 'formik'

import { mapDayToFrench } from 'pages/VenueCreation/OpeningHoursReadOnly/utils'
import { DayCheckbox } from 'screens/IndividualOffer/StocksEventCreation/DayCheckbox'
import { RecurrenceDays } from 'screens/IndividualOffer/StocksEventCreation/form/types'

import { VenueEditionFormValues } from '../types'

import styles from './OpeningHoursForm.module.scss'

export function OpeningHoursForm() {
  const {
    values: { days },
  } = useFormikContext<VenueEditionFormValues>()

  return (
    <>
      <fieldset className={styles['day-inputs']}>
        <div className={styles['legend-wrapper']}>
          <legend className={styles['legend']}>
            Sélectionner vos jours d’ouverture :
          </legend>
        </div>
        <DayCheckbox
          letter="L"
          label="Lundi"
          name="days"
          value={RecurrenceDays.MONDAY}
          className={styles['day-checkbox']}
        />
        <DayCheckbox
          letter="M"
          label="Mardi"
          name="days"
          value={RecurrenceDays.TUESDAY}
          className={styles['day-checkbox']}
        />
        <DayCheckbox
          letter="M"
          label="Mercredi"
          name="days"
          value={RecurrenceDays.WEDNESDAY}
          className={styles['day-checkbox']}
        />
        <DayCheckbox
          letter="J"
          label="Jeudi"
          name="days"
          value={RecurrenceDays.THURSDAY}
          className={styles['day-checkbox']}
        />
        <DayCheckbox
          letter="V"
          label="Vendredi"
          name="days"
          value={RecurrenceDays.FRIDAY}
          className={styles['day-checkbox']}
        />
        <DayCheckbox
          letter="S"
          label="Samedi"
          name="days"
          value={RecurrenceDays.SATURDAY}
          className={styles['day-checkbox']}
        />
        <DayCheckbox
          letter="D"
          label="Dimanche"
          name="days"
          value={RecurrenceDays.SUNDAY}
          className={styles['day-checkbox']}
        />
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

const daysOfWeek = [
  'monday',
  'tuesday',
  'wednesday',
  'thursday',
  'friday',
  'saturday',
  'sunday',
]
