import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import Draggable from 'react-draggable'

import DuoOfferContainer from '../../../../layout/DuoOffer/DuoOfferContainer'
import Icon from '../../../../layout/Icon/Icon'
import Price from '../../../../layout/Price/Price'
import FinishableContainer from '../../../../layout/Finishable/FinishableContainer'
import { getPageY } from '../../../../../utils/getPageY'

const toRectoDraggableBounds = {
  bottom: 0,
  left: 0,
  right: 0,
  top: 0,
}

class Navigation extends PureComponent {
  handleStopDrag = event => {
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

  handleFlipCardAndTrackOfferConsultation = () => {
    const { flipHandler, trackConsultOffer } = this.props
    trackConsultOffer()
    flipHandler()
  }

  render() {
    const {
      distanceClue,
      flipHandler,
      offerId,
      priceRange,
      separator,
    } = this.props

    return (
      <div id="deck-navigation">
        <div className="controls flex-columns items-end wrap-3 mosaicx2-background">
          {this.renderPreviousButton()}
          {(flipHandler && (
            <div className="flex-rows">
              <Draggable
                axis="y"
                bounds={toRectoDraggableBounds}
                onStop={this.handleStopDrag}
              >
                <div id="dragButton">
                  <button
                    className="button to-recto"
                    id="deck-open-verso-button"
                    onClick={this.handleFlipCardAndTrackOfferConsultation}
                    onDragLeave={this.handleFlipCardAndTrackOfferConsultation}
                    type="button"
                  >
                    <Icon
                      alt="Plus d'infos"
                      className=" "
                      svg="ico-slideup-w"
                    />
                  </button>
                  <div className="clue">
                    <FinishableContainer>
                      <Price
                        free="Gratuit"
                        id="deck-navigation-offer-price"
                        value={priceRange}
                      />
                      {offerId && <DuoOfferContainer offerId={offerId} />}
                      <div className="separator">
                        {separator}
                      </div>
                      <div>
                        {distanceClue}
                      </div>
                    </FinishableContainer>
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

Navigation.defaultProps = {
  distanceClue: null,
  flipHandler: null,
  handleGoNext: null,
  handleGoPrevious: null,
  offerId: '',
  priceRange: null,
  verticalSlideRatio: 0.3,
}

Navigation.propTypes = {
  distanceClue: PropTypes.string,
  flipHandler: PropTypes.func,
  handleGoNext: PropTypes.func,
  handleGoPrevious: PropTypes.func,
  height: PropTypes.number.isRequired,
  offerId: PropTypes.string,
  priceRange: PropTypes.arrayOf(PropTypes.number),
  separator: PropTypes.string.isRequired,
  trackConsultOffer: PropTypes.func.isRequired,
  verticalSlideRatio: PropTypes.number,
}

export default Navigation
