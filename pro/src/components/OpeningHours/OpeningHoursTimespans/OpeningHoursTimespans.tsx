import classNames from 'classnames'
import fullLessIcon from 'icons/full-less.svg'
import fullMoreIcon from 'icons/full-more.svg'
import { useFieldArray, useFormContext } from 'react-hook-form'

import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import { TimePicker } from '@/ui-kit/form/TimePicker/TimePicker'
import { ListIconButton } from '@/ui-kit/ListIconButton/ListIconButton'

import styles from './OpeningHoursTimespans.module.scss'

export function OpeningHoursTimespans({
  weekDay,
  hasTimespans,
  dayFrenchName,
  hasErrorBecauseOfEmptyOpeningHours,
}: {
  weekDay: keyof WeekdayOpeningHoursTimespans
  hasTimespans: boolean
  dayFrenchName: string
  hasErrorBecauseOfEmptyOpeningHours: boolean
}) {
  const form = useFormContext<{
    openingHours: WeekdayOpeningHoursTimespans | null
  }>()

  const timespans = useFieldArray({
    name: `openingHours.${weekDay}`,
  })

  if (!hasTimespans) {
    return (
      <div className={styles['no-timespans']}>
        <span>Fermé</span>
        <ListIconButton
          icon={fullMoreIcon}
          tooltipContent={`Ajouter une plage horaire le ${dayFrenchName.toLowerCase()}`}
          onClick={() => timespans.append([['', '']])}
          aria-invalid={hasErrorBecauseOfEmptyOpeningHours}
        />
      </div>
    )
  }

  return timespans.fields.map((field, i) => {
    const hasOverlappingTimespans =
      form.formState.errors.openingHours?.[weekDay]?.root?.message

    return (
      <div className={styles['timespan']} key={field.id}>
        <div className={styles['timespan-inputs']}>
          <TimePicker
            label="Ouvre à"
            required
            isLabelHidden={i === 1}
            className={styles['time-picker']}
            {...form.register(`openingHours.${weekDay}.${i}.0`)}
            error={
              form.formState.errors.openingHours?.[weekDay]?.[i]?.[0]
                ?.message ||
              //  Display the overlapping error message on the first time of the second span
              (i === 1 ? hasOverlappingTimespans : '')
            }
          />
          <span
            className={classNames(styles['timespan-separator'], {
              [styles['first-timespan']]: i === 0,
            })}
          >
            -
          </span>
          <TimePicker
            label="Ferme à"
            required
            className={styles['time-picker']}
            isLabelHidden={i === 1}
            {...form.register(`openingHours.${weekDay}.${i}.1`)}
            error={
              form.formState.errors.openingHours?.[weekDay]?.[i]?.[1]?.message
            }
          />
        </div>

        <div
          className={classNames(styles['timespan-actions'], {
            [styles['first-timespan']]: i === 0,
          })}
        >
          {timespans.fields.length > 0 && (
            <ListIconButton
              icon={fullLessIcon}
              tooltipContent={`Supprimer la ${timespans.fields.length > 1 ? (i === 0 ? 'première ' : 'deuxième ') : ''}plage horaire du ${dayFrenchName.toLowerCase()}`}
              onClick={() => timespans.remove(i)}
            />
          )}
          {timespans.fields.length < 2 && (
            <ListIconButton
              icon={fullMoreIcon}
              tooltipContent={`Ajouter une plage horaire le ${dayFrenchName.toLowerCase()}`}
              onClick={() => timespans.append([['', '']])}
            />
          )}
        </div>
      </div>
    )
  })
}
