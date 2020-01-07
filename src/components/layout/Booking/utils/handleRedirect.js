const handleRedirect = (booking, match, location) => {
  const { url } = match
  const { search } = location
  let nextUrl

  if (url.includes('recherche-algolia')) {
    nextUrl = url.replace('/reservation', '') + search
  } else if (url.includes('reservations')) {
    nextUrl = `/reservations/details/${booking.id}`
  } else {
    nextUrl = url.split(/\/reservation(\/|$|\/$)/)[0]
  }
  return nextUrl
}

export default handleRedirect
