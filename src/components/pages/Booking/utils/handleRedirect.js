const handleRedirect = (booking, match) => {
  const { url } = match
  let nextUrl = url.split(/\/reservation(\/|$|\/$)/)[0]

  if (url.includes('reservations')) {
    if (booking) {
      nextUrl = '/reservations/details/' + booking.id
    }
  }
  return nextUrl
}

export default handleRedirect
