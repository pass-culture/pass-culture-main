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
      de {openingHoursForDay[0][0]} à {openingHoursForDay[0][1]}
      {openingHoursForDay.length > 1 && (
        <>
          {' '}
          et de {openingHoursForDay[1][0]} à {openingHoursForDay[1][1]}
        </>
      )}
    </>
  )
}
