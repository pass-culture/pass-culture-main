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
      {openingHoursForDay[0][0]}-{openingHoursForDay[0][1]}
      {openingHoursForDay.length > 1 && (
        <>
          {' '}
          et {openingHoursForDay[1][0]}-{openingHoursForDay[1][1]}
        </>
      )}
    </>
  )
}
