import styles from './OpeningHoursReadOnlyHours.module.scss'

export function OpeningHoursReadOnlyHours({
  openingHoursForDay,
}: {
  openingHoursForDay?: string[][] | null
}) {
  if (!openingHoursForDay || openingHoursForDay.length === 0) {
    return
  }
  return (
    <>
      de <span className={styles['important']}>{openingHoursForDay[0][0]}</span>{' '}
      à <span className={styles['important']}>{openingHoursForDay[0][1]}</span>
      {openingHoursForDay.length > 1 && (
        <>
          {' '}
          et de{' '}
          <span className={styles['important']}>
            {openingHoursForDay[1][0]}
          </span>{' '}
          à{' '}
          <span className={styles['important']}>
            {openingHoursForDay[1][1]}
          </span>
        </>
      )}
    </>
  )
}
