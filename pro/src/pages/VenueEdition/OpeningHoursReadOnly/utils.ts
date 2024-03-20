export function mapDayToFrench(
  day: string
):
  | 'Lundi'
  | 'Mardi'
  | 'Mercredi'
  | 'Jeudi'
  | 'Vendredi'
  | 'Samedi'
  | 'Dimanche' {
  switch (day.toUpperCase()) {
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
