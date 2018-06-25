import get from 'lodash.get'
import { createSelector } from 'reselect'

const createSelectEvent = () => createSelector(
  state => get(state, 'data.events', []),
  (state, eventId) => eventId,
  (events, eventId) => events.find(event =>
    event.id === eventId
  )
)
export default createSelectEvent

// export const selectCurrentEvent = createSelectEvent()
