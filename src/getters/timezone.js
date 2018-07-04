export default function getTimezone(venue) {
  console.log("VENUE", venue)
  if (!venue)
      return
    switch(venue.departementCode) {
        case '97':
        case '973':
          return 'UTC+3' // POSIX compatibility requires that the offsets are inverted.
        default:
          return 'Europe/Paris'
  }
}
