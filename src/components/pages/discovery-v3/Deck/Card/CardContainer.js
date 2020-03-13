import moment from 'moment'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'
import { compose } from 'redux'
import { mergeData, requestData } from 'redux-thunk-data'

import Card from './Card'
import { getRecommendationSelectorByCardPosition } from '../../utils/utils'
import { recommendationNormalizer } from '../../../../../utils/normalizers'

export const mapStateToProps = (state, ownProps) => {
  const { match, position } = ownProps
  const { params } = match
  const { mediationId, offerId } = params
  const recommendationSelector = getRecommendationSelectorByCardPosition(position)
  const recommendation = recommendationSelector(state, offerId, mediationId)
  return {
    recommendation,
  }
}

export const mapDispatchToProps = dispatch => ({
  handleClickRecommendation: recommendation => {
    dispatch(
      requestData({
        apiPath: `recommendations/${recommendation.id}`,
        body: { isClicked: true },
        method: 'PATCH',
        normalizer: recommendationNormalizer,
      })
    )
  },

  handleReadRecommendation: recommendation => {
    const readRecommendation = {
      dateRead: moment.utc().toISOString(),
      id: recommendation.id,
    }
    dispatch(
      mergeData({
        readRecommendations: [readRecommendation],
      })
    )
  },
})

const mapSizeToProps = ({ width, height }) => ({
  height,
  width: Math.min(width, 500),
})

export default compose(
  withSizes(mapSizeToProps),
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Card)
