import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import RectoContainer from '../../../../layout/Recto/RectoContainer'
import VersoContainer from '../../../../layout/Verso/VersoContainer'
import isDetailsView from '../../../../../helpers/isDetailsView'
import { getHeaderColor } from '../../../../../utils/colors'

class Card extends PureComponent {
  componentDidMount() {
    const { handleReadRecommendation, position, recommendation } = this.props

    const isFirstHasJustBeenRead = position === 'previous'
    if (isFirstHasJustBeenRead) {
      handleReadRecommendation(recommendation)
    }
  }

  componentDidUpdate(prevProps) {
    const {
      handleClickRecommendation,
      handleReadRecommendation,
      match,
      recommendation,
      position,
    } = this.props
    const areDetailsNowVisible = isDetailsView(match) && !isDetailsView(prevProps.match)

    const isCurrent = recommendation && position === 'current'

    const hasJustBeenRead =
      position === 'previous' &&
      (recommendation && recommendation.id) !==
        (prevProps.recommendation && prevProps.recommendation.id)
    if (hasJustBeenRead) {
      handleReadRecommendation(recommendation)
    }

    if (!isCurrent) return

    const shouldRequest = areDetailsNowVisible && !recommendation.isClicked
    if (!shouldRequest) return

    handleClickRecommendation(recommendation)
  }

  render() {
    const { match, position, recommendation, width } = this.props
    const { firstThumbDominantColor, index } = recommendation || {}
    const areDetails = isDetailsView(match)
    const headerColor = getHeaderColor(firstThumbDominantColor)
    const isCurrent = position === 'current'
    const translateTo = index * width
    return (
      <div
        className={`card ${isCurrent ? 'current' : ''}`}
        style={{
          backgroundColor: headerColor || '#000',
          transform: `translate(${translateTo}px, 0)`,
        }}
      >
        {recommendation && isCurrent && <VersoContainer areDetailsVisible={areDetails} />}
        {recommendation && (
          <RectoContainer
            areDetailsVisible={areDetails}
            recommendation={recommendation}
          />
        )}
      </div>
    )
  }
}

Card.defaultProps = {
  recommendation: null,
}

Card.propTypes = {
  handleClickRecommendation: PropTypes.func.isRequired,
  handleReadRecommendation: PropTypes.func.isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  position: PropTypes.string.isRequired,
  recommendation: PropTypes.shape(),
  width: PropTypes.number.isRequired,
}

export default Card
