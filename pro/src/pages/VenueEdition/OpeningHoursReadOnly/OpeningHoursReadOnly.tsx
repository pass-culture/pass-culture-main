import { GetVenueResponseModel } from 'apiClient/v1'
import { mapDayToFrench } from 'commons/utils/date'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

import styles from './OpeningHoursReadOnly.module.scss'

type OpeningHours = {
  openingHours: GetVenueResponseModel['openingHours']
}

type OpenClose = {
  open: string
  close: string
}

type HoursProps = {
  hours: Array<OpenClose>
}

export function OpeningHoursReadOnly({ openingHours }: OpeningHours) {
  const filledDays = Object.entries(openingHours ?? {}).filter((dateAndHour) =>
    Boolean(dateAndHour[1])
  )

  if (!openingHours || filledDays.length === 0) {
    return (
      <SummarySubSection
        title={'Horaires d’ouverture'}
        shouldShowDivider={false}
      >
        <p>
          {openingHours === null
            ? 'Non renseigné'
            : `Vous n’avez pas renseigné d’horaire d’ouverture. Votre établissement est indiqué comme fermé sur l’application.`}
        </p>
      </SummarySubSection>
    )
  }
  return (
    <SummarySubSection title={'Horaires d’ouverture'} shouldShowDivider={false}>
      <SummaryDescriptionList
        descriptions={filledDays.map((dateAndHour) => {
          return {
            title: mapDayToFrench(dateAndHour[0]),
            text: <Hours hours={dateAndHour[1]} />,
          }
        })}
      />
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
