import { SummaryDescriptionList } from 'components/SummaryLayout/SummaryDescriptionList'
import { SummarySubSection } from 'components/SummaryLayout/SummarySubSection'

import styles from './OpeningHoursReadOnly.module.scss'

type OpeningHours = {
  openingHours: Array<Record<string, any>>
}

export function OpeningHoursReadOnly({ openingHours }: OpeningHours) {
  return (
    <SummarySubSection title={'Horaires d’ouverture'}>
      <SummaryDescriptionList
        descriptions={openingHours
          .filter((dateAndHour) => dateAndHour && Object.values(dateAndHour)[0])
          .map((dateAndHour) => {
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

function mapDayToFrench(
  day: string
):
  | 'Lundi'
  | 'Mardi'
  | 'Mercredi'
  | 'Jeudi'
  | 'Vendredi'
  | 'Samedi'
  | 'Dimanche' {
  switch (day) {
    case 'MONDAY':
      return 'Lundi'
    case 'TUESDAY':
      return 'Mardi'
    case 'WEDNESDAY':
      return 'Mercredi'
    case 'THURSDAY':
      return 'Jeudi'
    case 'FRIDAY':
      return 'Vendredi'
    case 'SATURDAY':
      return 'Samedi'
    case 'SUNDAY':
      return 'Dimanche'
    default:
      return 'Dimanche'
  }
}
