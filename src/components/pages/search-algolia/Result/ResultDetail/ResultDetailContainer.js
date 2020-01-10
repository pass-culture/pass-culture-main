import { compose } from 'redux'
import { connect } from 'react-redux'
import { requestData } from 'redux-thunk-data'
import { withRouter } from 'react-router-dom'

import DetailsContainer from '../../../../layout/Details/DetailsContainer'
import { offerNormalizer } from '../../../../../utils/normalizers'

export const mapDispatchToProps = dispatch => {
  return {
    getOfferById: offerId => {
      dispatch(
        requestData({
          apiPath: '/offers/' + offerId,
          method: 'GET',
          normalizer: offerNormalizer,
        })
      )
    },
  }
}

export default compose(
  withRouter,
  connect(
    null,
    mapDispatchToProps
  )
)(DetailsContainer)
