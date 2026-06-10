interface OpeningHoursRowProps {
  openingHoursForDay: string[][] | null | undefined
}
export const OpeningHoursRow = ({
  openingHoursForDay,
}: Readonly<OpeningHoursRowProps>) => {
  if (!openingHoursForDay || openingHoursForDay.length === 0) {
    return null
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
