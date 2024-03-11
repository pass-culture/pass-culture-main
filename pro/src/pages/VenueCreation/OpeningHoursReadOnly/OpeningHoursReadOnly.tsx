import styles from './OpeningHoursReadOnly.module.scss'

type OpeningHours = {
  openingHours: Array<Record<string, any>>
}

export function OpeningHoursReadOnly({ openingHours }: OpeningHours) {
  return openingHours.map((row) => (
    <DayAndHours
      day={Object.keys(row)[0]}
      hours={Object.values(row)[0]}
      key={Object.keys(row)[0]}
    />
  ))
}

export function DayAndHours({ day, hours }: DayAndHours) {
  const displayedDay = mapDayToFrench(day)
  if (!hours) {
    return <></>
  }

  return (
    <>
      {hours.length === 1 ? (
        <p className={styles['day-and-hours']}>
          <span className={styles['day']}>
            {displayedDay}
            {' : '}
          </span>{' '}
          de <span className={styles['important']}>{hours[0].open}</span> à{' '}
          <span className={styles['important']}>{hours[0].close}</span>
        </p>
      ) : (
        <p className={styles['day-and-hours']}>
          <span className={styles['day']}>
            {displayedDay}
            {' : '}
          </span>{' '}
          de <span className={styles['important']}>{hours[0].open}</span> à{' '}
          <span className={styles['important']}>{hours[0].close}</span> et de{' '}
          <span className={styles['important']}>{hours[1].open}</span> à{' '}
          <span className={styles['important']}>{hours[1].close}</span>{' '}
        </p>
      )}
    </>
  )
}

type openClose = {
  open: string
  close: string
}

type DayAndHours = {
  day: string
  hours: Array<openClose> | null
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
