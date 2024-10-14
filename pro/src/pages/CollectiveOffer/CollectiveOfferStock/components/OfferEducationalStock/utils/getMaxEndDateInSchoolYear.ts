const SEPTEMBER = 8
const AUGUST = 7

export const getMaxEndDateInSchoolYear = (startDatetime: string) => {
  const startDate = new Date(startDatetime)
  const startYear = startDate.getFullYear()
  const endYear = startDate.getMonth() >= SEPTEMBER ? startYear + 1 : startYear
  return new Date(endYear, AUGUST, 31)
}
