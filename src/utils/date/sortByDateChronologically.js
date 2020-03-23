export const sortByDateChronologically = () => items =>
  items.sort((a, b) => {
    const datea = a.beginningDatetime
    const dateb = b.beginningDatetime
    if (datea === dateb) return 0
    else if (!datea) return 1
    else if (!dateb) return -1
    else if (datea.isAfter(dateb)) return 1
    else if (datea.isBefore(dateb)) return -1
    return 0
  })
