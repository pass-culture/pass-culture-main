import { GetVenueResponseModel } from 'apiClient/v1'
import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

import styles from './OpeningHoursReadOnly.module.scss'
import { mapDayToFrench } from './utils'

type OpeningHours = {
  openingHours: GetVenueResponseModel['venueOpeningHours']
}

export function OpeningHoursReadOnly({ openingHours }: OpeningHours) {
  return (
    <SummarySubSection title={'Horaires d’ouverture'}>
      <SummaryDescriptionList
        descriptions={(
          openingHours?.filter(
            (dateAndHour) => dateAndHour && Object.values(dateAndHour)[0]
          ) ?? []
        ).map((dateAndHour) => {
          return {
            title: mapDayToFrench(Object.keys(dateAndHour)[0]),
            text: <Hours hours={Object.values(dateAndHour)[0]} />,
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
