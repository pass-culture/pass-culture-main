import { AppSearchFields } from '../constants'

export const buildBoosts = position => {
  if (
    !position ||
    typeof position.latitude !== 'number' ||
    typeof position.longitude !== 'number'
  ) {
    return
  }
  return {
    [AppSearchFields.venue_position]: {
      type: 'proximity',
      function: 'exponential',
      center: `${position.latitude},${position.longitude}`,
      factor: 10,
    },
  }
}
