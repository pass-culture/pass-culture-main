import { Icon } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'

import Price from './Price'
import Finishable from './layout/Finishable'
import { getHeaderColor } from '../utils/colors'
import { getPriceRangeFromStocks, isRecommendationFinished } from '../helpers'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import { ROOT_PATH } from '../utils/config'

const DeckNavigation = ({
  isFinished,
  headerColor,
  recommendation,
  flipHandler,
  handleGoNext,
  handleGoPrevious,
  transitionTimeout,
}) => {
  const { distance, offer } = recommendation || {}
  const priceRange = getPriceRangeFromStocks(offer && offer.stocks)
  const color = headerColor || '#000'
  const backgroundGradient = `linear-gradient(to bottom, rgba(0,0,0,0) 0%,${color} 30%,${color} 100%)`
  return (
    <div id="deck-navigation" style={{ background: backgroundGradient }}>
      <div
        className="controls flex-columns wrap-3"
        style={{ backgroundImage: `url('${ROOT_PATH}/mosaic-w@2x.png')` }}
      >
        {/* previous button */}
        {(handleGoPrevious && (
          <button
            type="button"
            className="button before"
            onClick={handleGoPrevious}
          >
            <Icon svg="ico-prev-w-group" alt="Précédent" />
          </button>
        )) || <span />}
        {/* flip button */}
        {(flipHandler && (
          <div className="flex-rows">
            <button
              type="button"
              onClick={flipHandler}
              onDragLeave={flipHandler}
              className="button to-recto"
            >
              <Icon svg="ico-slideup-w" alt="Plus d'infos" />
            </button>
            <div
              className="clue"
              style={{ transition: `opacity ${transitionTimeout}ms` }}
            >
              <Finishable finished={isFinished}>
                <Price value={priceRange} />
                <div className="separator">
                  {offer ? '\u00B7' : ' '}
                </div>
                <div>
                  {offer ? distance : ' '}
                </div>
              </Finishable>
            </div>
          </div>
        )) || <span />}
        {/* next button */}
        {(handleGoNext && (
          <button type="button" className="button after" onClick={handleGoNext}>
            <Icon svg="ico-next-w-group" alt="Suivant" />
          </button>
        )) || <span />}
      </div>
    </div>
  )
}

DeckNavigation.defaultProps = {
  flipHandler: null,
  handleGoNext: null,
  handleGoPrevious: null,
  headerColor: null,
  isFinished: null,
  recommendation: null,
  transitionTimeout: 250,
}

DeckNavigation.propTypes = {
  flipHandler: PropTypes.func,
  handleGoNext: PropTypes.func,
  handleGoPrevious: PropTypes.func,
  headerColor: PropTypes.string,
  isFinished: PropTypes.bool,
  recommendation: PropTypes.object,
  transitionTimeout: PropTypes.number,
}

export default compose(
  withRouter,
  connect((state, ownProps) => {
    const { mediationId, offerId } = ownProps.match.params
    const recommendation = currentRecommendationSelector(
      state,
      offerId,
      mediationId
    )
    const isFinished = isRecommendationFinished(recommendation, offerId)
    const headerColor = getHeaderColor(recommendation.firstThumbDominantColor)
    return {
      headerColor,
      isFinished,
      recommendation,
    }
  })
)(DeckNavigation)
