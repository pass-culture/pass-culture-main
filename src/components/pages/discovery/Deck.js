import get from 'lodash.get'
import { Icon } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Draggable from 'react-draggable'
import { connect } from 'react-redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'
import { compose } from 'redux'

import Card from './Card'
import DeckNavigation from './DeckNavigation'
import { NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD } from '../../../helpers/discovery'
import {
  closeCardDetails,
  showCardDetails,
  flipUnflippable,
} from '../../../reducers/card'
import currentRecommendationSelector from '../../../selectors/currentRecommendation'
import nextRecommendationSelector from '../../../selectors/nextRecommendation'
import previousRecommendationSelector from '../../../selectors/previousRecommendation'
import selectRecommendationsForDiscovery from '../../../selectors/recommendations'

export class RawDeck extends Component {
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
    // const withRecommendationsAvailable = isRecommendations(
    //   recommendations,
    //   previousProps
    // )
    // const withCurrentRecommandationAvailable = isCurrentRecommendation(
    //   currentRecommendation,
    //   previousProps
    // )
    // const withNewRecommendationsAvailable = isNewRecommendations(
    //   recommendations,
    //   previousProps
    // )
    // const withNewCurrentRecommandationAvailable = isNewCurrentRecommendation(
    //   currentRecommendation,
    //   previousProps
    // )

    const { match } = this.props
    const { view } = match.params
    const isVersoView = view === 'verso'
    if (isVersoView) return
    this.handleUrlFlip()

    // if (
    //   !withRecommendationsAvailable ||
    //   !withCurrentRecommandationAvailable ||
    //   !withNewRecommendationsAvailable ||
    //   !withNewCurrentRecommandationAvailable
    // ) {
    //   this.handleRefreshedDraggableKey()
    // }
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
      this.handleClosecardDetails()
    } else if (data.y < -height * verticalSlideRatio) {
      this.handleShowcardDetails()
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
    history.push(`/decouverte/${offerId || 'tuto'}/${mediationId || ''}`)
    this.handleRefreshNext()
  }

  handleGoPrevious = () => {
    const { history, areDetailsVisible, previousRecommendation } = this.props
    if (!previousRecommendation || areDetailsVisible) return
    const { offerId, mediationId } = previousRecommendation
    history.push(`/decouverte/${offerId || 'tuto'}/${mediationId || ''}`)
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

  handleShowcardDetails = () => {
    const { dispatch, isFlipDisabled } = this.props
    if (isFlipDisabled) return
    dispatch(showCardDetails())
  }

  handleClosecardDetails = () => {
    const { dispatch, unFlippable } = this.props
    if (unFlippable) return
    dispatch(closeCardDetails())
  }

  handleUrlFlip = () => {
    // Quand on arrive depuis un booking vers une offre, le details doit être affiché
    const { dispatch, match } = this.props
    const { view } = match.params
    const isVersoView = view === 'verso'
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
            onClick={this.handleClosecardDetails}
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
              (!isFlipDisabled && this.handleShowcardDetails) || null
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

RawDeck.defaultProps = {
  currentRecommendation: null,
  horizontalSlideRatio: 0.2,
  nextRecommendation: null,
  noDataTimeout: 20000,
  previousRecommendation: null,
  readTimeout: 2000,
  verticalSlideRatio: 0.1,
}

RawDeck.propTypes = {
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

const mapStateToProps = (state, ownProps) => {
  const { mediationId, offerId } = ownProps.match.params
  const currentRecommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  )
  const { mediation } = currentRecommendation || {}
  const { thumbCount, tutoIndex } = mediation || {}

  const recommendations = selectRecommendationsForDiscovery(state)
  const nbRecos = recommendations ? recommendations.length : 0

  const isFlipDisabled =
    !currentRecommendation || (typeof tutoIndex === 'number' && thumbCount <= 1)

  const nextLimit =
    nbRecos > 0 &&
    (NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD >= nbRecos - 1
      ? nbRecos - 1
      : nbRecos - 1 - NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD)

  const previousLimit =
    nbRecos > 0 &&
    (NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD < nbRecos - 1
      ? NB_CARDS_REMAINING_THAT_TRIGGERS_LOAD + 1
      : 0)

  return {
    areDetailsVisible: state.card.areDetailsVisible,
    currentRecommendation,
    draggable: state.card.draggable,
    isEmpty: get(state, 'loading.config.isEmpty'),
    isFlipDisabled,
    nextLimit,
    nextRecommendation: nextRecommendationSelector(state, offerId, mediationId),
    previousLimit,
    previousRecommendation: previousRecommendationSelector(
      state,
      offerId,
      mediationId
    ),
    recommendations,
    unFlippable: state.card.unFlippable,
  }
}

const mapSizeToProps = ({ width, height }) => ({
  height,
  // NOTE -> CSS body{ max-width: 500px; }
  width: Math.min(width, 500),
})

const Deck = compose(
  withRouter,
  withSizes(mapSizeToProps),
  connect(mapStateToProps)
)(RawDeck)

export default Deck
