import withSelectors from './withSelectors'
import { THUMBS_URL } from '../utils/config'

const withFrontendOffer = withSelectors({
  thingOrEventOccurence: [
    ownProps => ownProps.eventOccurence,
    ownProps => ownProps.thing,
    (eventOccurence, thing) => eventOccurence || thing,
  ],
  thumbUrl: [
    ownProps => ownProps.thumbCount,
    ownProps => ownProps.id,
    ownProps => ownProps.eventOccurence,
    ownProps => ownProps.thing,
    (thumbCount, id, eventOccurence, thing) =>
      thumbCount > 0
        ? `${THUMBS_URL}/offers/${id}`
        : eventOccurence && eventOccurence.thumbCount > 0
          ? `${THUMBS_URL}/events/${eventOccurence.id}`
          : thing && thing.thumbCount > 0 && `${THUMBS_URL}/things/${thing.id}`,
  ],
  type: [
    (ownProps, nextState) => nextState.thingOrEventOccurence,
    thingOrEventOccurence => thingOrEventOccurence.type,
  ],
})

export default withFrontendOffer
