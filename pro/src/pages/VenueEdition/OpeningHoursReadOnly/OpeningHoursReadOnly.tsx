import { GetVenueResponseModel } from 'apiClient/v1'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

import styles from './OpeningHoursReadOnly.module.scss'
import { mapDayToFrench } from './utils'

type OpeningHours = {
  openingHours: GetVenueResponseModel['openingHours']
}

export function OpeningHoursReadOnly({ openingHours }: OpeningHours) {
  const filledDays = Object.entries(openingHours ?? {}).filter((dateAndHour) =>
    Boolean(dateAndHour[1])
  )

  if (!openingHours || filledDays.length === 0) {
    return (
      <SummarySubSection title={'Horaires d’ouverture'}>
        <p>Vous n’avez pas renseigné d’horaires d’ouverture.</p>
      </SummarySubSection>
    )
  }
  return (
    <SummarySubSection title={'Horaires d’ouverture'}>
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

export function Hours({ hours }: Hours) {
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

type openClose = {
  open: string
  close: string
}

type Hours = {
  hours: Array<openClose>
}
