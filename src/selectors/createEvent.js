import get from 'lodash.get'
import { createSelector } from 'reselect'

const createSelectEvent = () => createSelector(
  state => get(state, 'data.events', []),
  (state, params) => params,
  (events, {type, id}) => events.find(event =>
    type === 'event' && event.id === id
  )
)
export default createSelectEvent

// export const selectCurrentEvent = createSelectEvent()
