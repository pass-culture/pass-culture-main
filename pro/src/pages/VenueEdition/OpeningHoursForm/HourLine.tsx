import { useFormikContext } from 'formik'
import { useState } from 'react'

import fullLessIcon from 'icons/full-less.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button, TimePicker } from 'ui-kit'
import { ButtonVariant } from 'ui-kit/Button/types'

import { VenueEditionFormValues } from '../types'

import styles from './OpeningHoursForm.module.scss'

export function HourLine({
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
