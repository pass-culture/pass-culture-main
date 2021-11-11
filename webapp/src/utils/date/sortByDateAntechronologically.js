import moment from 'moment'

export const sortByDateAntechronologically = (a, b) => {
  const datea = moment(a.dateCreated)
  const dateb = moment(b.dateCreated)
  if (!datea || !dateb) return 0
  if (datea.isAfter(dateb)) return -1
  if (datea.isBefore(dateb)) return 1
  return 0
}
