export const getDatesInInterval = (start: Date, end: Date): Date[] => {
  const dates = []
  let currentDate = start
  while (currentDate <= end) {
    dates.push(currentDate)
    // Clone date object to avoid mutating old one
    currentDate = new Date(currentDate)
    currentDate.setDate(currentDate.getDate() + 1)
  }
  return dates
}
