import withSelectors from './withSelectors'
import { API_URL, THUMBS_URL } from '../utils/config'

const withFrontendOffer = withSelectors({
  workOrEvent: [
    ownProps => ownProps.work,
    ownProps => ownProps.event,
    (work, event) => work || event
  ],
  description: [
    ownProps => ownProps.description,
    (ownProps, nextState) => nextState.workOrEvent,
    ownProps => ownProps.event,
    (description, workOrEvent) => description || workOrEvent.description
  ],
  name: [
    (ownProps, nextState) => nextState.workOrEvent,
    workOrEvent => workOrEvent.name
  ],
  thumbUrl: [
    ownProps => ownProps.hasThumb,
    ownProps => ownProps.id,
    ownProps => ownProps.work,
    (hasThumb, id, work) => hasThumb
      ? `${THUMBS_URL}/offers/${id}`
      : (
        work && work.hasThumb
          ? `${THUMBS_URL}/works/${work.id}`
          : `${API_URL}/static/images/default_thumb.png`
      )
  ],
  type: [
    (ownProps, nextState) => nextState.workOrEvent,
    workOrEvent => workOrEvent.type
  ],
})



export default withFrontendOffer
