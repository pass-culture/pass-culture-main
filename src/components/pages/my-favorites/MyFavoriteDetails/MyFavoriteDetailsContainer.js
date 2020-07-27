import { connect } from 'react-redux'
import { compose } from 'redux'
import { requestData } from 'redux-thunk-data'

import { offerNormalizer } from '../../../../utils/normalizers'
import withRequiredLogin from '../../../hocs/with-login/withRequiredLogin'
import DetailsContainer from '../../../layout/Details/DetailsContainer'

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
)(DetailsContainer)
