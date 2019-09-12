export const isReserved = status =>
  !(status.length > 0 && status[0].class.match('cancelled|finished|fully-booked'))

export const reservationStatus = (
  isActive,
  isFinished,
  isFullyBooked,
  hasBookings,
  isBooked,
  humanizeRelativeDate
) => {
  const status = []

  if (isFinished) {
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

  if (isFullyBooked) {
    return [
      {
        label: 'Épuisé',
        class: 'fully-booked',
      },
    ]
  }

  if (hasBookings && isBooked) {
    status.push({
      label: 'Réservé',
      class: 'booked',
    })
  }

  if (humanizeRelativeDate) {
    if (humanizeRelativeDate === 'Demain') {
      status.push({
        label: humanizeRelativeDate,
        class: 'tomorrow',
      })
    } else {
      status.push({
        label: humanizeRelativeDate,
        class: 'today',
      })
    }
  }

  return status
}
