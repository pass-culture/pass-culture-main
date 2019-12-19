import { withRouter } from 'react-router-dom'

import DetailsContainer from '../../../../layout/Details/DetailsContainer'
import { requestData } from 'redux-thunk-data'
import { offerNormalizer } from '../../../../../utils/normalizers'
import { connect } from 'react-redux'
import { compose } from 'redux'

export const mapDispatchToProps = dispatch => {
  return {
    getOfferById: (offerId) => {
      dispatch(
        requestData({
          apiPath: '/offers/' + offerId,
          method: 'GET',
          normalizer: offerNormalizer,
        }))
    }
  }
}

export default compose(
  withRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(DetailsContainer)
