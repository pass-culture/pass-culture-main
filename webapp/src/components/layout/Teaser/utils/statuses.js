export const isReserved = statuses =>
  !(statuses.length > 0 && statuses[0].class.match('cancelled|finished|fully-booked'))

export const reservationStatuses = (
  isActive,
  hasBookingLimitDatetimesPassed,
  hasBookings,
  humanizeRelativeDate,
  isBooked = false
) => {
  const statuses = []

  if (hasBookingLimitDatetimesPassed) {
    return [
      {
        label: 'Terminé',
        class: 'finished',
      },
    ]
  }

  if (!isActive || (hasBookings && !isBooked)) {
    return [
      {
        label: 'Annulé',
        class: 'cancelled',
      },
    ]
  }

  if (hasBookings && isBooked) {
    statuses.push({
      label: 'Réservé',
      class: 'booked',
    })
  }

  if (humanizeRelativeDate) {
    if (humanizeRelativeDate === 'Demain') {
      statuses.push({
        label: humanizeRelativeDate,
        class: 'tomorrow',
      })
    } else {
      statuses.push({
        label: humanizeRelativeDate,
        class: 'today',
      })
    }
  }

  return statuses
}
