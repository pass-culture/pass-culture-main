import { GetVenueResponseModel } from 'apiClient/v1'
import { mapDayToFrench , DAYS_IN_ORDER } from 'commons/utils/date'
import { getFormattedAddress } from 'commons/utils/getFormattedAddress'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'
import { SummarySubSubSection } from 'components/SummaryLayout/SummarySubSubSection'

import styles from './OpeningHoursReadOnly.module.scss'

type OpeningHours = {
  isOpenToPublicEnabled: boolean
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

type Entries<T> = T extends Record<infer W, infer U> ? [W, U][] : never;
type OpeningHoursEntries = Entries<GetVenueResponseModel['openingHours']>;

export function OpeningHoursReadOnly({
  isOpenToPublicEnabled,
  openingHours,
  address,
}: OpeningHours) {
  const filledDays = Object.entries(openingHours ?? {})
    .filter((dateAndHour) =>
      Boolean(dateAndHour[1])
    )

  const orderedFilledDays = DAYS_IN_ORDER.map(d => {
    const index = filledDays.findIndex(([day]) => day === d)
    return index === -1 ? null : filledDays[index]
  }).filter(Boolean) as OpeningHoursEntries

  const OpeningHours = () => <SummaryDescriptionList
    descriptions={orderedFilledDays.map((dateAndHour) => {
      return {
        title: mapDayToFrench(dateAndHour[0]),
        text: <Hours hours={dateAndHour[1]} />,
      }
    })}
  />

  if (isOpenToPublicEnabled) {
    return <SummarySubSubSection title="Adresse et horaires">
      <span className={styles['opening-hours-address']}>
        {`Adresse : ${getFormattedAddress(address)}`}
      </span>
      {orderedFilledDays.length === 0 ? (
        <span>
          {openingHours === null
            ? 'Horaires : Non renseigné'
            : `Horaires : Vous n’avez pas renseigné d’horaire d’ouverture. Votre établissement est indiqué comme fermé sur l’application.`}
        </span>
      ) : <OpeningHours />}
    </SummarySubSubSection>
  } else {
    return <SummarySubSection title="Horaires d'ouverture">
      {orderedFilledDays.length === 0 ? (
        <p>
          {openingHours === null
            ? 'Non renseigné'
            : `Vous n’avez pas renseigné d’horaire d’ouverture. Votre établissement est indiqué comme fermé sur l’application.`}
        </p>
      ) : <OpeningHours />}
    </SummarySubSection>
  }
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
