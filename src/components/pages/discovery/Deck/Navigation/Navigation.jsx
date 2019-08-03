import get from 'lodash.get'
import PropTypes from 'prop-types'
import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import { compose } from 'redux'
import Draggable from 'react-draggable'

import Icon from '../../layout/Icon'
import Price from '../../layout/Price'
import Finishable from '../../layout/Finishable'
import { getHeaderColor } from '../../../utils/colors'
import { getPriceRangeFromStocks } from '../../../helpers'
import { isRecommendationOfferFinished } from '../../../helpers/isRecommendationOfferFinished'
import { ROOT_PATH } from '../../../utils/config'
import { getPageY } from '../../../utils/getPageY'

const toRectoDraggableBounds = {
  bottom: 0,
  left: 0,
  right: 0,
  top: 0,
}

export class RawDeckNavigation extends React.PureComponent {
  handleOnStop = event => {
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
          className="button before"
          onClick={handleGoPrevious}
          type="button"
        >
          <Icon
            alt="Précédent"
            svg="ico-prev-w-group"
          />
        </button>
      )) || <span />
    )
  }

  renderNextButton = () => {
    const { handleGoNext } = this.props
    return (
      (handleGoNext && (
        <button
          className="button after"
          onClick={handleGoNext}
          type="button"
        >
          <Icon
            alt="Suivant"
            svg="ico-next-w-group"
          />
        </button>
      )) || <span />
    )
  }

  render() {
    const { isFinished, recommendation, flipHandler, transitionTimeout } = this.props

    const { distance, offer } = recommendation || {}
    let distanceClue = ' '
    if (offer && offer.venue) {
      distanceClue = offer.venue.isVirtual ? 'offre en ligne' : distance
    }
    const firstThumbDominantColor = get(recommendation, 'firstThumbDominantColor')
    const headerColor = getHeaderColor(firstThumbDominantColor)
    const priceRange = getPriceRangeFromStocks(offer && offer.stocks)

    const backgroundGradient = `linear-gradient(to bottom, rgba(0,0,0,0) 0%,${headerColor} 30%,${headerColor} 100%)`
    return (
      <div
        id="deck-navigation"
        style={{ background: backgroundGradient }}
      >
        <div
          className="controls flex-columns items-end wrap-3"
          style={{ backgroundImage: `url('${ROOT_PATH}/mosaic-w@2x.png')` }}
        >
          {this.renderPreviousButton()}
          {(flipHandler && (
            <div className="flex-rows">
              <Draggable
                axis="y"
                bounds={toRectoDraggableBounds}
                onStop={this.handleOnStop}
              >
                <div id="dragButton">
                  <button
                    className="button to-recto"
                    id="deck-open-verso-button"
                    onClick={flipHandler}
                    onDragLeave={flipHandler}
                    type="button"
                  >
                    <Icon
                      alt="Plus d'infos"
                      className=" "
                      svg="ico-slideup-w"
                    />
                  </button>
                  <div
                    className="clue"
                    style={{ transition: `opacity ${transitionTimeout}ms` }}
                  >
                    <Finishable finished={isFinished}>
                      <Price
                        free="Gratuit"
                        id="deck-navigation-offer-price"
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
  isFinished: false,
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
  recommendation: PropTypes.shape(),
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
