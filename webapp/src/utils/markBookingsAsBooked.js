export const markAsBooked = bookings => {
  const bookingsStockIds = bookings.map(({ stockId }) => stockId)
  return items =>
    items.map(obj => {
      const isBooked = (bookingsStockIds || []).includes(obj.id)
      return Object.assign({}, obj, {
        userHasAlreadyBookedThisDate: isBooked,
      })
    })
}
