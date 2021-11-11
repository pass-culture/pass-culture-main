import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import { requestData } from '../../../utils/fetch-normalize-data/requestData'
import isCancelView from '../../../utils/isCancelView'
import { offerNormalizer } from '../../../utils/normalizers'
import Details from './Details'

export const mapStateToProps = (state, ownProps) => {
  const { match } = ownProps
  const cancelView = isCancelView(match)

  return {
    cancelView,
  }
}

export const mapDispatchToProps = dispatch => ({
  getOfferById: offerId => {
    dispatch(
      requestData({
        apiPath: `/offers/${offerId}`,
        normalizer: offerNormalizer,
      })
    )
  },
})

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Details)
