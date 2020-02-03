import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'

import Offer from './Offer'
import { offerNormalizer } from '../../../utils/normalizers'
import withRequiredLogin from '../../hocs/with-login/withRequiredLogin'

export const mapDispatchToProps = (dispatch, ownProps) => ({
  getOfferById: () => {
    const {
      match: {
        params: { offerId },
      },
    } = ownProps

    dispatch(
      requestData({
        apiPath: `/offers/${offerId}`,
        normalizer: offerNormalizer,
      })
    )
  },
})

export default compose(
  withRequiredLogin,
  connect(
    null,
    mapDispatchToProps
  )
)(Offer)
