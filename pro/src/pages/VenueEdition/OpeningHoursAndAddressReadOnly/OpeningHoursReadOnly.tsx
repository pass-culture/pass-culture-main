import type { WeekdayOpeningHoursTimespans } from '@/apiClient/v1'
import { mapDayToFrench, OPENING_HOURS_DAYS } from '@/commons/utils/date'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'
import { areOpeningHoursEmpty } from '@/pages/IndividualOffer/IndividualOfferTimetable/commons/areOpeningHoursEmpty'

import { OpeningHoursReadOnlyHours } from './OpeningHoursReadOnlyHours/OpeningHoursReadOnlyHours'

export const OpeningHoursReadOnly = ({
  openingHours,
}: {
  openingHours?: WeekdayOpeningHoursTimespans | null
}) => {
  const orderedFilledDays = OPENING_HOURS_DAYS.map((d) => ({
    day: d,
    openingHours: openingHours?.[d],
  })) satisfies {
    openingHours: WeekdayOpeningHoursTimespans['MONDAY']
    day: string
  }[]

  return areOpeningHoursEmpty(openingHours) ? (
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
