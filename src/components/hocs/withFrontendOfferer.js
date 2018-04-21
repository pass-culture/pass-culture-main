import withSelectors from './withSelectors'
import { THUMBS_URL } from '../../utils/config'

const withFrontendOfferer = withSelectors({
  thumbUrl: [
    ownProps => ownProps.thumbCount,
    ownProps => ownProps.id,
    (thumbCount, id) => thumbCount > 0 && `${THUMBS_URL}/offerers/${id}`,
  ],
})

export default withFrontendOfferer
