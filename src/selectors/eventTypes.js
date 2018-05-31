import { createSelector } from 'reselect'

export default createSelector(
  state => state.data.eventTypes,
  eventTypes =>
    eventTypes && eventTypes.map(eventType => {
      switch(eventType) {
        case '':
          return
        default:
          return eventType
      }
    })
)
