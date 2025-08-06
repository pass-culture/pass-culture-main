import { GetVenueResponseModel } from '@/apiClient/v1'
import { DAYS_IN_ORDER, mapDayToFrench } from '@/commons/utils/date'
import { getFormattedAddress } from '@/commons/utils/getFormattedAddress'
import { SummaryDescriptionList } from '@/components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSubSection } from '@/components/SummaryLayout/SummarySubSubSection'

import styles from './OpeningHoursReadOnly.module.scss'

type OpeningHours = {
  openingHours: GetVenueResponseModel['openingHours']
  address?: GetVenueResponseModel['address']
}

type OpenClose = {
  open: string
  close: string
}

type HoursProps = {
  hours: Array<OpenClose>
}

type Entries<T> = T extends Record<infer W, infer U> ? [W, U][] : never
type OpeningHoursEntries = Entries<GetVenueResponseModel['openingHours']>

export function OpeningHoursReadOnly({ openingHours, address }: OpeningHours) {
  const filledDays = Object.entries(openingHours ?? {}).filter((dateAndHour) =>
    Boolean(dateAndHour[1])
  )

  const orderedFilledDays = DAYS_IN_ORDER.map((d) => {
    const index = filledDays.findIndex(([day]) => day === d)
    return index === -1 ? null : filledDays[index]
  }).filter(Boolean) as OpeningHoursEntries

  const OpeningHours = () => (
    <SummaryDescriptionList
      descriptions={orderedFilledDays.map((dateAndHour) => {
        return {
          title: mapDayToFrench(dateAndHour[0]),
          text: <Hours hours={dateAndHour[1]} />,
        }
      })}
    />
  )

  return (
    <SummarySubSubSection title="Adresse et horaires">
      <span className={styles['opening-hours-address']}>
        {`Adresse : ${getFormattedAddress(address)}`}
      </span>
      {orderedFilledDays.length === 0 ? (
        <span>
          {openingHours === null
            ? 'Horaires : Non renseigné'
            : `Horaires : Vous n’avez pas renseigné d’horaire d’ouverture. Votre établissement est indiqué comme fermé sur l’application.`}
        </span>
      ) : (
        <OpeningHours />
      )}
    </SummarySubSubSection>
  )
}

export function Hours({ hours }: HoursProps) {
  return (
    <>
      {hours.length === 1 ? (
        <>
          de <span className={styles['important']}>{hours[0].open}</span> à{' '}
          <span className={styles['important']}>{hours[0].close}</span>
        </>
      ) : (
        <>
          de <span className={styles['important']}>{hours[0].open}</span> à{' '}
          <span className={styles['important']}>{hours[0].close}</span> et de{' '}
          <span className={styles['important']}>{hours[1].open}</span> à{' '}
          <span className={styles['important']}>{hours[1].close}</span>{' '}
        </>
      )}
    </>
  )
}
