import { createSelector } from 'reselect'

export default venueSelector => createSelector(
  venueSelector,
  venue => {
      if (!venue)
        return
      switch(venue.departementCode) {
          case '97':
          case '973':
            return 'America/Cayenne' // POSIX compatibility requires that the offsets are inverted.
          default:
            return 'Europe/Paris'
      }
  }
)
