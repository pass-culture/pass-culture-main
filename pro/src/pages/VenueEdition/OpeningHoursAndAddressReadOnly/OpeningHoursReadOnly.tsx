import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import { mapDayToFrench, OPENING_HOURS_DAYS } from '@/commons/utils/date'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'

import { OpeningHoursReadOnlyHours } from './OpeningHoursReadOnlyHours/OpeningHoursReadOnlyHours'

function areOpeningHoursEmpty(
  openingHours?: WeekdayOpeningHoursTimespans | null
) {
  if (!openingHours) {
    return true
  }

  return Object.values(openingHours).every((day) => !day || day.length === 0)
}

export const OpeningHoursReadOnly = ({
  openingHours,
}: {
  openingHours?: WeekdayOpeningHoursTimespans | null
}) => {
  const openingHoursEmpty = areOpeningHoursEmpty(openingHours)

  const orderedFilledDays = OPENING_HOURS_DAYS.map((d) => ({
    day: d,
    openingHours: openingHours?.[d],
  })) satisfies {
    openingHours: WeekdayOpeningHoursTimespans['MONDAY']
    day: string
  }[]

  return openingHoursEmpty ? (
    <span>
      Horaires : Vos horaires d’ouverture ne sont pas affichées sur
      l'application car votre établissement est indiqué comme fermé tous les
      jours.
    </span>
  ) : (
    <SummaryDescriptionList
      descriptions={orderedFilledDays
        .filter((d) => Boolean(d.openingHours))
        .map((dateAndHour) => {
          return {
            title: mapDayToFrench(dateAndHour.day),
            text: (
              <OpeningHoursReadOnlyHours
                openingHoursForDay={dateAndHour.openingHours}
              />
            ),
          }
        })}
    />
  )
}
