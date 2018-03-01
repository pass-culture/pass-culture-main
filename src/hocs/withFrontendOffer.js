import withSelectors from './withSelectors'
import { API_URL, THUMBS_URL } from '../utils/config'

const withFrontendOffer = withSelectors({
  thingOrEventOccurence: [
    ownProps => ownProps.eventOccurence,
    ownProps => ownProps.thing,
    (eventOccurence, thing) => eventOccurence || thing
  ],
  description: [
    ownProps => ownProps.description,
    (ownProps, nextState) => nextState.thingOrEventOccurence,
    (description, thingOrEventOccurence) => description || thingOrEventOccurence.description
  ],
  name: [
    ownProps => ownProps.name,
    (ownProps, nextState) => nextState.thingOrEventOccurence,
    (name, thingOrEventOccurence) => name || thingOrEventOccurence.name
  ],
  thumbUrl: [
    ownProps => ownProps.thumbCount,
    ownProps => ownProps.id,
    ownProps => ownProps.eventOccurence,
    ownProps => ownProps.thing,
    (thumbCount, id, eventOccurence, thing) => thumbCount > 0
      ? `${THUMBS_URL}/offers/${id}`
      : (
        eventOccurence && eventOccurence.thumbCount > 0
          ? `${THUMBS_URL}/events/${eventOccurence.id}`
          : (
            thing && thing.thumbCount > 0
            ? `${THUMBS_URL}/things/${thing.id}`
            : `${API_URL}/static/images/default_thumb.png`
          )
      )
  ],
  type: [
    (ownProps, nextState) => nextState.thingOrEventOccurence,
    thingOrEventOccurence => thingOrEventOccurence.type
  ]
})



export default withFrontendOffer
