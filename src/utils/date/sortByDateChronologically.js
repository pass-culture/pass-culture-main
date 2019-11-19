export const sortByDateChronologically = () => items =>
  items.sort((a, b) => {
    const datea = a.beginningDatetime
    const dateb = b.beginningDatetime
    if (!datea || !dateb) return 0
    if (datea.isAfter(dateb)) return 1
    if (datea.isBefore(dateb)) return -1
    return 0
  })
