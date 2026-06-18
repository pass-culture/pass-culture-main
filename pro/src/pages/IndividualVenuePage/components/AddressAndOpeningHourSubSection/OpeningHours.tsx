import type {
  GetVenueResponseModel,
  WeekdayOpeningHoursTimespans,
} from '@/apiClient/v1'
import { mapDayToFrench, OPENING_HOURS_DAYS } from '@/commons/utils/date'
import { areOpeningHoursEmpty } from '@/pages/VenueEdition/commons/areOpeningHoursEmpty'
import { SummaryDescriptionList } from '@/ui-kit/SummaryLayout/SummaryDescriptionList'

import { OpeningHoursRow } from './OpeningHoursRow'

interface OpeningHoursProps {
  openingHours: GetVenueResponseModel['openingHours']
}
export const OpeningHours = ({ openingHours }: Readonly<OpeningHoursProps>) => {
  const orderedFilledDays = OPENING_HOURS_DAYS.map((d) => ({
    day: d,
    openingHours: openingHours?.[d],
  })) satisfies {
    day: string
    openingHours: WeekdayOpeningHoursTimespans['MONDAY']
  }[]

  if (areOpeningHoursEmpty(openingHours)) {
    return (
      <span>
        Horaires : Vos horaires d’ouverture ne sont pas affichées sur
        l'application car votre établissement est indiqué comme fermé tous les
        jours.
      </span>
    )
  }

  return (
    <SummaryDescriptionList
      descriptions={orderedFilledDays
        .filter((d) => Boolean(d.openingHours))
        .map((dateAndHour) => {
          return {
            title: mapDayToFrench(dateAndHour.day),
            text: (
              <OpeningHoursRow openingHoursForDay={dateAndHour.openingHours} />
            ),
          }
        })}
    />
  )
}
