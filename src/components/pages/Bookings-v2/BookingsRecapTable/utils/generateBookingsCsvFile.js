import moment from 'moment'
import { FORMAT_DD_MM_YYYY_HH_mm } from '../../../../../utils/date'
import { getBookingStatusDisplayInformationsOrDefault } from '../CellsFormatter/utils/bookingStatusConverter'

export const CSV_HEADERS = [
  'Nom de l’offre',
  'Date de l\'évènement',
  'Nom et prénom du bénéficiaire',
  'Email du bénéficiaire',
  'Date et heure de réservation',
  'Contremarque',
  'Statut de la contremarque',
]

const generateBookingsCsvFile = bookings => {
  let csv_data = [CSV_HEADERS]

  bookings.forEach(booking => {
    const bookingArray = []

    bookingArray.push(booking.stock.offer_name)

    if (booking.stock.type === 'event') {
      const eventDatetimeFormatted = moment.parseZone(booking.stock.event_beginning_datetime).format(FORMAT_DD_MM_YYYY_HH_mm)
      bookingArray.push(eventDatetimeFormatted)
    } else {
      bookingArray.push('')
    }

    bookingArray.push(booking.beneficiary.lastname.concat(' ', booking.beneficiary.firstname))
    bookingArray.push(booking.beneficiary.email)
    const bookingDatetimeFormatted = moment.parseZone(booking.booking_date).format(FORMAT_DD_MM_YYYY_HH_mm)
    bookingArray.push(bookingDatetimeFormatted)
    bookingArray.push(booking.booking_token)
    const bookingStatus = getBookingStatusDisplayInformationsOrDefault(booking.booking_status)
    bookingArray.push(bookingStatus.status)
    csv_data.push(bookingArray)
  })
  return csv_data
}

export default generateBookingsCsvFile
