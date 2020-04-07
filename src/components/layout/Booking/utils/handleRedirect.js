const handleRedirect = (match, location) => {
  const { url, params } = match
  const { search } = location
  const { bookingId } = params
  let nextUrl

  if (url.includes('recherche-offres')) {
    nextUrl = url.replace('/reservation', '') + search
  } else if (url.includes('reservations')) {
    nextUrl = `/reservations/details/${bookingId}`
  } else {
    nextUrl = url.split(/\/reservation(\/|$|\/$)/)[0]
  }
  return nextUrl
}

export default handleRedirect
