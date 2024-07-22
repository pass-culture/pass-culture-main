import cn from 'classnames'
import { useFormikContext } from 'formik'
import { useState } from 'react'

import fullLessIcon from 'icons/full-less.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'
import { mapDayToFrench } from 'utils/date'

import { Day, VenueEditionFormValues } from '../types'

import styles from './OpeningHoursForm.module.scss'

type HourLineProps = {
  day: Day
}

export function HourLine({ day }: HourLineProps) {
  const { setFieldValue, values, setFieldTouched } =
    useFormikContext<VenueEditionFormValues>()
  const [isFullLineDisplayed, setIsFullLineDisplayed] = useState(
    Boolean(values[day].afternoonStartingHour)
  )

  async function removeAfternoon() {
    setIsFullLineDisplayed(false)

    await setFieldValue(`${day}.afternoonStartingHour`, '')
    await setFieldValue(`${day}.afternoonEndingHour`, '')
    await setFieldValue(`${day}.isAfternoonOpen`, false)
  }

  return (
    <>
      <tr className={styles['row-data']}>
        <th
          scope="row"
          rowSpan={isFullLineDisplayed ? 2 : 1}
          className={styles['day-cell']}
        >
          {mapDayToFrench(day)}
        </th>
        <td
          className={cn(styles['hour-cell'], {
            [styles['hour-cell-afternoon-displayed'] ?? '']:
              isFullLineDisplayed,
          })}
        >
          <TimePicker
            label="Horaire d’ouverture 1"
            name={`${day}.morningStartingHour`}
            isLabelHidden
            hideFooter
            className={styles['time-picker']}
          />
        </td>
        <td
          className={cn(styles['hour-cell'], {
            [styles['hour-cell-afternoon-displayed'] ?? '']:
              isFullLineDisplayed,
          })}
        >
          <span className={styles['second-hour']}>
            <span className={styles['top-aligned-content']}>-</span>
            <TimePicker
              label="Horaire de fermeture 1"
              name={`${day}.morningEndingHour`}
              isLabelHidden
              hideFooter
              className={styles['time-picker']}
              min={values[day].morningStartingHour}
            />
          </span>
        </td>
        <td
          className={cn(styles['hour-cell'], {
            [styles['hour-cell-afternoon-displayed'] ?? '']:
              isFullLineDisplayed,
          })}
        >
          {!isFullLineDisplayed && (
            <Button
              variant={ButtonVariant.TERNARY}
              className={styles['top-aligned-button']}
              icon={fullMoreIcon}
              onClick={async () => {
                await setFieldValue(`${day}.isAfternoonOpen`, true)
                await setFieldTouched(`${day}.afternoonStartingHour`, false)
                await setFieldTouched(`${day}.afternoonEndingHour`, false)
                setIsFullLineDisplayed(true)
              }}
              hasTooltip
            >
              Ajouter une plage horaire
            </Button>
          )}
        </td>
      </tr>
      {isFullLineDisplayed && (
        <tr className={styles['row-data']}>
          <td className={styles['hour-cell']}>
            <TimePicker
              label="Horaire d’ouverture 2"
              name={`${day}.afternoonStartingHour`}
              isLabelHidden
              hideFooter
              className={styles['time-picker']}
              min={values[day].morningEndingHour}
            />
          </td>
          <td className={styles['hour-cell']}>
            <span className={styles['second-hour']}>
              <span className={styles['top-aligned-content']}>-</span>
              <TimePicker
                label="Horaire de fermeture 2"
                name={`${day}.afternoonEndingHour`}
                isLabelHidden
                hideFooter
                className={styles['time-picker']}
                min={values[day].afternoonStartingHour}
              />
            </span>
          </td>
          <td scope="row" className={styles['hour-cell']}>
            <Button
              className={styles['top-aligned-button']}
              variant={ButtonVariant.TERNARY}
              icon={fullLessIcon}
              onClick={removeAfternoon}
              hasTooltip
            >
              Supprimer la plage horaire
            </Button>
          </td>
        </tr>
      )}
    </>
  )
}
