import { useFormikContext } from 'formik'
import { useState } from 'react'

import fullLessIcon from 'icons/full-less.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { mapDayToFrench } from 'pages/VenueEdition/OpeningHoursReadOnly/utils'
import { DayCheckbox } from 'screens/IndividualOffer/StocksEventCreation/DayCheckbox'
import { Button, TimePicker } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

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
        <ul>
          {days
            .sort((a, b) => daysOfWeek.indexOf(a) - daysOfWeek.indexOf(b))
            .map((day) => (
              <li key={day}>
                <fieldset className={styles['inputs-line']}>
                  <div className={styles['legend-wrapper']}>
                    <legend className={styles['legend-hours']}>
                      {mapDayToFrench(day)}
                    </legend>
                  </div>
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
                  />
                </fieldset>
              </li>
            ))}
        </ul>
      )}
    </>
  )
}

function HourLine({
  day,
}: {
  day:
    | 'monday'
    | 'tuesday'
    | 'wednesday'
    | 'thursday'
    | 'friday'
    | 'saturday'
    | 'sunday'
}) {
  const { setFieldValue, initialValues } =
    useFormikContext<VenueEditionFormValues>()
  const [isFullLineDisplayed, setIsFullLineDisplayed] = useState(
    Boolean(initialValues[day].afternoonStartingHour)
  )

  async function removeAfternoon() {
    setIsFullLineDisplayed(false)

    await setFieldValue(`${day}.afternoonStartingHour`, '')
    await setFieldValue(`${day}.afternoonEndingHour`, '')
  }

  return (
    <span className={styles['hour-line']}>
      <TimePicker
        label={'Horaire d’ouverture 1'}
        name={`${day}.morningStartingHour`}
        isLabelHidden
        hideFooter
        inline
        className={styles['time-picker']}
      />
      -
      <TimePicker
        label={'Horaire de fermeture 1'}
        name={`${day}.morningEndingHour`}
        isLabelHidden
        hideFooter
        inline
        className={styles['time-picker']}
      />{' '}
      {isFullLineDisplayed && (
        <>
          |
          <TimePicker
            label={'Horaire d’ouverture 2'}
            name={`${day}.afternoonStartingHour`}
            isLabelHidden
            hideFooter
            inline
            className={styles['time-picker']}
          />
          -
          <TimePicker
            label={'Horaire de fermeture 2'}
            name={`${day}.afternoonEndingHour`}
            isLabelHidden
            hideFooter
            inline
            className={styles['time-picker']}
          />
        </>
      )}
      {isFullLineDisplayed ? (
        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullLessIcon}
          onClick={removeAfternoon}
          hasTooltip
        >
          Supprimer la plage horaire
        </Button>
      ) : (
        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullMoreIcon}
          onClick={() => setIsFullLineDisplayed(true)}
          hasTooltip
        >
          Ajouter une plage horaire
        </Button>
      )}
    </span>
  )
}
