import withSelectors from './withSelectors'
import { API_URL, THUMBS_URL } from '../utils/config'

const withThumbUrl = withSelectors({
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
  ]
})



export default withThumbUrl
