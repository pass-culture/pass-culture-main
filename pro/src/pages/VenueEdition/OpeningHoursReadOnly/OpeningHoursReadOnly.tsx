import { GetVenueResponseModel } from 'apiClient/v1'
import { mapDayToFrench , DAYS_IN_ORDER } from 'commons/utils/date'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

import styles from './OpeningHoursReadOnly.module.scss'

type OpeningHours = {
  isOpenToPublicEnabled: boolean
  isOpenToPublic: boolean
  openingHours: GetVenueResponseModel['openingHours']
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

export function OpeningHoursReadOnly({ isOpenToPublicEnabled, isOpenToPublic, openingHours }: OpeningHours) {
  const filledDays = Object.entries(openingHours ?? {})
    .filter((dateAndHour) =>
      Boolean(dateAndHour[1])
    )

  const orderedFilledDays = DAYS_IN_ORDER.map(d => {
    const index = filledDays.findIndex(([day]) => day === d)
    return index === -1 ? null : filledDays[index]
  }).filter(Boolean) as OpeningHoursEntries

  return (
    <SummarySubSection
      title={isOpenToPublicEnabled ? "Accès et horaires" : "Horaires d'ouverture"}
      shouldShowDivider={false}
    >
      {isOpenToPublicEnabled && !isOpenToPublic ? (
        <p>
          Accueil du public dans la structure : Non
        </p>
      ) : (!openingHours || orderedFilledDays.length === 0) ? (
        <p>
          {openingHours === null
            ? 'Non renseigné'
            : `Vous n’avez pas renseigné d’horaire d’ouverture. Votre établissement est indiqué comme fermé sur l’application.`}
        </p>
      ) : (
        <SummaryDescriptionList
          descriptions={orderedFilledDays.map((dateAndHour) => {
            return {
              title: mapDayToFrench(dateAndHour[0]),
              text: <Hours hours={dateAndHour[1]} />,
            }
          })}
        />
      )}
    </SummarySubSection>
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
