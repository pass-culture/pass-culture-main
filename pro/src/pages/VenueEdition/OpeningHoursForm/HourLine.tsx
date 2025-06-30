import cn from 'classnames'
import { useState } from 'react'
import { useFormContext } from 'react-hook-form'

import { mapDayToFrench } from 'commons/utils/date'
import fullLessIcon from 'icons/full-less.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { Button } from 'ui-kit/Button/Button'
import { ButtonVariant } from 'ui-kit/Button/types'
import { TimePicker } from 'ui-kit/form/TimePicker/TimePicker'

import { Day, VenueEditionFormValues } from '../types'

import styles from './OpeningHoursForm.module.scss'

type HourLineProps = {
  day: Day
}

export function HourLine({ day }: HourLineProps) {
  const {
    setValue,
    watch,
    register,
    formState: { errors },
  } = useFormContext<VenueEditionFormValues>()

  const values = watch()
  const [isFullLineDisplayed, setIsFullLineDisplayed] = useState(
    Boolean(values[day]?.afternoonStartingHour)
  )

  function removeAfternoon() {
    setIsFullLineDisplayed(false)

    setValue(`${day}.afternoonStartingHour`, '')
    setValue(`${day}.afternoonEndingHour`, '')
    setValue(`${day}.isAfternoonOpen`, false)
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
            [styles['hour-cell-afternoon-displayed']]: isFullLineDisplayed,
          })}
        >
          <TimePicker
            label="Horaire d’ouverture 1"
            {...register(`${day}.morningStartingHour`)}
            className={styles['time-picker']}
            error={errors[`${day}`]?.morningStartingHour?.message}
            isLabelHidden
          />
        </td>
        <td
          className={cn(styles['hour-cell'], {
            [styles['hour-cell-afternoon-displayed']]: isFullLineDisplayed,
          })}
        >
          <span className={styles['second-hour']}>
            <span className={styles['top-aligned-content']}>-</span>
            <TimePicker
              label="Horaire de fermeture 1"
              {...register(`${day}.morningEndingHour`)}
              className={styles['time-picker']}
              suggestedTimeList={{ min: values[day]?.morningStartingHour }}
              error={errors[`${day}`]?.morningEndingHour?.message}
              isLabelHidden
            />
          </span>
        </td>
        <td
          className={cn(styles['hour-cell'], {
            [styles['hour-cell-afternoon-displayed']]: isFullLineDisplayed,
          })}
        >
          {!isFullLineDisplayed && (
            <Button
              variant={ButtonVariant.TERNARY}
              className={styles['top-aligned-button']}
              icon={fullMoreIcon}
              onClick={() => {
                setValue(`${day}.isAfternoonOpen`, true)
                setIsFullLineDisplayed(true)
              }}
              tooltipContent="Ajouter une plage horaire"
            />
          )}
        </td>
      </tr>
      {isFullLineDisplayed && (
        <tr className={styles['row-data']}>
          <td className={styles['hour-cell']}>
            <TimePicker
              label="Horaire d’ouverture 2"
              {...register(`${day}.afternoonStartingHour`)}
              className={styles['time-picker']}
              suggestedTimeList={{ min: values[day]?.morningEndingHour }}
              error={errors[`${day}`]?.afternoonStartingHour?.message}
              isLabelHidden
            />
          </td>
          <td className={styles['hour-cell']}>
            <span className={styles['second-hour']}>
              <span className={styles['top-aligned-content']}>-</span>
              <TimePicker
                label="Horaire de fermeture 2"
                {...register(`${day}.afternoonEndingHour`)}
                className={styles['time-picker']}
                suggestedTimeList={{ min: values[day]?.afternoonStartingHour }}
                error={errors[`${day}`]?.afternoonEndingHour?.message}
                isLabelHidden
              />
            </span>
          </td>
          <td scope="row" className={styles['hour-cell']}>
            <Button
              className={styles['top-aligned-button']}
              variant={ButtonVariant.TERNARY}
              icon={fullLessIcon}
              onClick={removeAfternoon}
              tooltipContent={<>Supprimer la plage horaire</>}
            />
          </td>
        </tr>
      )}
    </>
  )
}
