import get from 'lodash.get'
import { Icon } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Draggable from 'react-draggable'

import Card from '../card'
import DeckNavigation from '../DeckNavigation'
import { shouldShowVerso } from '../../../../helpers'
import {
  closeCardDetails,
  flipUnflippable,
  showCardDetails,
} from '../../../../reducers/card'

class Deck extends Component {
  constructor(props) {
    super(props)
    this.currentReadRecommendationId = null
    this.state = { refreshKey: 0 }
  }

  componentDidMount() {
    const { currentRecommendation, recommendations } = this.props
    this.handleUrlFlip()

    const isStateWithoutRecommendationsOrCurrentRecommendation =
      !recommendations || recommendations.length === 0 || !currentRecommendation

    if (!isStateWithoutRecommendationsOrCurrentRecommendation) return
    this.handleRefreshedDraggableKey()
  }

  componentDidUpdate() {
    const { match } = this.props
    const isVersoView = shouldShowVerso(match)
    // prevents to be called twice at Mount and at Update
    if (isVersoView) return
    this.handleUrlFlip()
  }

  componentWillUnmount() {
    const { dispatch, readTimeout, noDataTimeout } = this.props
    dispatch(closeCardDetails())

    if (readTimeout) clearTimeout(readTimeout)
    if (noDataTimeout) clearTimeout(noDataTimeout)
  }

  onStop = (e, data) => {
    const {
      width,
      height,
      draggable,
      verticalSlideRatio,
      horizontalSlideRatio,
      currentRecommendation,
    } = this.props

    const index = get(currentRecommendation, 'index', 0)
    const offset = (data.x + width * index) / width
    if (draggable && data.y > height * verticalSlideRatio) {
      this.handleCloseCardDetails()
    } else if (data.y < -height * verticalSlideRatio) {
      this.handleShowCardDetails()
    } else if (offset > horizontalSlideRatio) {
      this.handleGoPrevious()
    } else if (-offset > horizontalSlideRatio) {
      this.handleGoNext()
    }
  }

  handleGoNext = () => {
    const { history, areDetailsVisible, nextRecommendation } = this.props
    if (!nextRecommendation || areDetailsVisible) return
    const { offerId, mediationId } = nextRecommendation
    history.push(
      `/decouverte/${offerId || 'tuto'}${(mediationId && `/${mediationId}`) ||
        ''}`
    )
    this.handleRefreshNext()
  }

  handleGoPrevious = () => {
    const { history, areDetailsVisible, previousRecommendation } = this.props
    if (!previousRecommendation || areDetailsVisible) return
    const { offerId, mediationId } = previousRecommendation
    history.push(
      `/decouverte/${offerId || 'tuto'}${(mediationId && `/${mediationId}`) ||
        ''}`
    )
  }

  handleRefreshNext = () => {
    const { currentRecommendation, handleDataRequest, nextLimit } = this.props
    const shouldRequest = nextLimit && currentRecommendation.index === nextLimit
    if (!shouldRequest) return
    handleDataRequest()
  }

  handleRefreshedDraggableKey = () => {
    this.setState(previousState => ({
      refreshKey: previousState.refreshKey + 1,
    }))
  }

  handleShowCardDetails = () => {
    const { dispatch, isFlipDisabled } = this.props
    if (isFlipDisabled) return
    dispatch(showCardDetails())
  }

  handleCloseCardDetails = () => {
    const { dispatch, unFlippable } = this.props
    if (unFlippable) return
    dispatch(closeCardDetails())
  }

  handleUrlFlip = () => {
    const { dispatch, match } = this.props
    const isVersoView = shouldShowVerso(match)
    if (!isVersoView) return
    dispatch(flipUnflippable())
  }

  renderDraggableCards() {
    const {
      areDetailsVisible,
      currentRecommendation,
      nextRecommendation,
      previousRecommendation,
      width,
    } = this.props
    const { index } = currentRecommendation || {}
    const { refreshKey } = this.state

    const position = {
      x: -1 * width * index,
      y: 0,
    }
    const draggableBounds = (areDetailsVisible && {}) || {
      bottom: 0,
      left: position.x - width,
      right: position.x + width,
      top: -100,
    }

    return (
      <Draggable
        speed={{ x: 5 }}
        key={refreshKey}
        position={position}
        onStop={this.onStop}
        bounds={draggableBounds}
        enableUserSelectHack={false}
        axis={areDetailsVisible ? 'none' : 'exclude'}
      >
        <div className="is-overlay">
          <div className="inner is-relative">
            {previousRecommendation && <Card position="previous" />}
            <Card position="current" />
            {nextRecommendation && <Card position="next" />}
          </div>
        </div>
      </Draggable>
    )
  }

  render() {
    const {
      currentRecommendation,
      height,
      nextRecommendation,
      isFlipDisabled,
      areDetailsVisible,
      previousRecommendation,
      recommendations,
      unFlippable,
    } = this.props

    const showCloseButton = areDetailsVisible && !unFlippable
    const showNavigation = !areDetailsVisible || isFlipDisabled

    return (
      <div
        id="deck"
        className="is-clipped is-relative"
        data-nb-recos={recommendations.length}
      >
        {showCloseButton && (
          <button
            type="button"
            className="close-button"
            id="deck-close-verso-button"
            onClick={this.handleCloseCardDetails}
            style={{ zIndex: 300 }}
          >
            <Icon svg="ico-close" alt="Fermer" />
          </button>
        )}
        {this.renderDraggableCards()}
        {showNavigation && currentRecommendation && (
          <DeckNavigation
            recommendation={currentRecommendation}
            flipHandler={
              (!isFlipDisabled && this.handleShowCardDetails) || null
            }
            handleGoNext={(nextRecommendation && this.handleGoNext) || null}
            handleGoPrevious={
              (previousRecommendation && this.handleGoPrevious) || null
            }
            height={height}
          />
        )}
      </div>
    )
  }
}

Deck.defaultProps = {
  currentRecommendation: null,
  horizontalSlideRatio: 0.2,
  nextRecommendation: null,
  noDataTimeout: 20000,
  previousRecommendation: null,
  readTimeout: 2000,
  verticalSlideRatio: 0.1,
}

Deck.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  currentRecommendation: PropTypes.object,
  dispatch: PropTypes.func.isRequired,
  draggable: PropTypes.bool.isRequired,
  handleDataRequest: PropTypes.func.isRequired,
  height: PropTypes.number.isRequired,
  history: PropTypes.object.isRequired,
  horizontalSlideRatio: PropTypes.number,
  isFlipDisabled: PropTypes.bool.isRequired,
  match: PropTypes.object.isRequired,
  nextLimit: PropTypes.oneOfType([PropTypes.bool, PropTypes.number]).isRequired,
  nextRecommendation: PropTypes.object,
  noDataTimeout: PropTypes.number,
  previousRecommendation: PropTypes.object,
  readTimeout: PropTypes.number,
  recommendations: PropTypes.array.isRequired,
  unFlippable: PropTypes.bool.isRequired,
  verticalSlideRatio: PropTypes.number,
  width: PropTypes.number.isRequired,
}

export default Deck
