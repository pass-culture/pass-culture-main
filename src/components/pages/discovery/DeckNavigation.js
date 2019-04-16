import get from 'lodash.get'
import { Icon } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import Draggable from 'react-draggable'

import Price from '../../layout/Price'
import Finishable from '../../layout/Finishable'
import { getHeaderColor } from '../../../utils/colors'
import { getPriceRangeFromStocks } from '../../../helpers'
import { isRecommendationOfferFinished } from '../../../helpers/isRecommendationOfferFinished'
import { ROOT_PATH } from '../../../utils/config'

const toRectoDraggableBounds = {
  bottom: 0,
  left: 0,
  right: 0,
  top: 0,
}

function getPageY(event) {
  if (window.TouchEvent && event instanceof TouchEvent) {
    const lastTouchIndex = event.changedTouches.length - 1
    return event.changedTouches[lastTouchIndex].pageY
  }

  return event.pageY
}

export class RawDeckNavigation extends React.PureComponent {
  onStop = event => {
    const { flipHandler, height, verticalSlideRatio } = this.props
    const shiftedDistance = height - getPageY(event)

    const thresholdDistance = height * verticalSlideRatio
    if (shiftedDistance > thresholdDistance) {
      // DON T KNOW YET HOW TO DO OTHERWISE:
      // IF IT IS CALLED DIRECTLY
      // THEN on unmount time of the component
      // one of the drag event handler will still complain
      // to want to do a setState while the component is now
      // unmounted...
      setTimeout(() => flipHandler())
    }
  }

  renderPreviousButton = () => {
    const { handleGoPrevious } = this.props
    return (
      (handleGoPrevious && (
        <button
          type="button"
          className="button before"
          onClick={handleGoPrevious}
        >
          <Icon svg="ico-prev-w-group" alt="Précédent" />
        </button>
      )) || <span />
    )
  }

  renderNextButton = () => {
    const { handleGoNext } = this.props
    return (
      (handleGoNext && (
        <button type="button" className="button after" onClick={handleGoNext}>
          <Icon svg="ico-next-w-group" alt="Suivant" />
        </button>
      )) || <span />
    )
  }

  render() {
    const {
      isFinished,
      recommendation,
      flipHandler,
      transitionTimeout,
    } = this.props

    const { distance, offer } = recommendation || {}
    let distanceClue = ' '
    if (offer && offer.venue) {
      distanceClue = offer.venue.isVirtual ? 'offre en ligne' : distance
    }
    const firstThumbDominantColor = get(
      recommendation,
      'firstThumbDominantColor'
    )
    const headerColor = getHeaderColor(firstThumbDominantColor)
    const priceRange = getPriceRangeFromStocks(offer && offer.stocks)

    const backgroundGradient = `linear-gradient(to bottom, rgba(0,0,0,0) 0%,${headerColor} 30%,${headerColor} 100%)`
    return (
      <div id="deck-navigation" style={{ background: backgroundGradient }}>
        <div
          className="controls flex-columns items-end wrap-3"
          style={{ backgroundImage: `url('${ROOT_PATH}/mosaic-w@2x.png')` }}
        >
          {/* previous button */}
          {this.renderPreviousButton()}
          {/* flip button */}
          {(flipHandler && (
            <div className="flex-rows">
              <Draggable
                bounds={toRectoDraggableBounds}
                onStop={this.onStop}
                axis="y"
              >
                <div id="dragButton">
                  <button
                    id="deck-open-verso-button"
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
                      <Price
                        id="deck-navigation-offer-price"
                        free="Gratuit"
                        value={priceRange}
                      />
                      <div className="separator">{offer ? '\u00B7' : ' '}</div>
                      <div>{distanceClue}</div>
                    </Finishable>
                  </div>
                </div>
              </Draggable>
            </div>
          )) || <span />}
          {/* next button */}
          {this.renderNextButton()}
        </div>
      </div>
    )
  }
}

RawDeckNavigation.defaultProps = {
  flipHandler: null,
  handleGoNext: null,
  handleGoPrevious: null,
  isFinished: null,
  recommendation: null,
  transitionTimeout: 250,
  verticalSlideRatio: 0.3,
}

RawDeckNavigation.propTypes = {
  flipHandler: PropTypes.func,
  handleGoNext: PropTypes.func,
  handleGoPrevious: PropTypes.func,
  height: PropTypes.number.isRequired,
  isFinished: PropTypes.bool,
  recommendation: PropTypes.object,
  transitionTimeout: PropTypes.number,
  verticalSlideRatio: PropTypes.number,
}

const mapStateToProps = (state, ownProps) => {
  const { recommendation } = ownProps
  const { offerId } = recommendation
  const isFinished = isRecommendationOfferFinished(recommendation, offerId)

  return {
    isFinished,
  }
}

const DeckNavigation = compose(
  withRouter,
  connect(mapStateToProps)
)(RawDeckNavigation)

export default DeckNavigation
