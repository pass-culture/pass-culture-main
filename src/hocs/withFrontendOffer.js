import withSelectors from './withSelectors'
import { API_URL, THUMBS_URL } from '../utils/config'

const withFrontendOffer = withSelectors({
  thingOrEvent: [
    ownProps => { console.log('ownProps', ownProps); return ownProps.thing },
    ownProps => ownProps.event,
    (thing, event) => thing || event
  ],
  description: [
    ownProps => ownProps.description,
    (ownProps, nextState) => nextState.thingOrEvent,
    (description, thingOrEvent) => description || thingOrEvent.description
  ],
  name: [
    ownProps => ownProps.name,
    (ownProps, nextState) => nextState.thingOrEvent,
    (name, thingOrEvent) => name || thingOrEvent.name
  ],
  thumbUrl: [
    ownProps => ownProps.thumbCount,
    ownProps => ownProps.id,
    ownProps => ownProps.event,
    ownProps => ownProps.thing,
    (thumbCount, id, event, thing) => thumbCount > 0
      ? `${THUMBS_URL}/offers/${id}`
      : (
        event && event.thumbCount > 0
          ? `${THUMBS_URL}/events/${event.id}`
          : (
            thing && thing.thumbCount > 0
            ? `${THUMBS_URL}/things/${thing.id}`
            : `${API_URL}/static/images/default_thumb.png`
          )
      )
  ],
  type: [
    (ownProps, nextState) => nextState.thingOrEvent,
    thingOrEvent => thingOrEvent.type
  ],
})



export default withFrontendOffer
