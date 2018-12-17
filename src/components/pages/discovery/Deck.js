import get from 'lodash.get'
import moment from 'moment'
import { mergeData, Logger, Icon } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import Draggable from 'react-draggable'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import withSizes from 'react-sizes'

import Card from './Card'
import DeckNavigation from './DeckNavigation'
import { flip, flipUnflippable, unFlip } from '../../../reducers/verso'
import currentRecommendationSelector from '../../../selectors/currentRecommendation'
import nextRecommendationSelector from '../../../selectors/nextRecommendation'
import previousRecommendationSelector from '../../../selectors/previousRecommendation'
import recommendationsSelector from '../../../selectors/recommendations'
import { PREVIOUS_NEXT_LIMIT } from '../../../utils/deck'

class Deck extends Component {
  constructor(props) {
    super(props)
    this.currentReadRecommendationId = null
    this.state = { refreshKey: 0 }
  }

  componentDidMount() {
    Logger.log('Deck ---> componentDidMount')
    const { currentRecommendation, history, recommendations } = this.props
    this.handleUrlFlip(history)
    if (!recommendations || !currentRecommendation) {
      // this.handleRefreshedData()
    }
  }

  componentDidUpdate(previousProps) {
    const { currentRecommendation, history, recommendations } = this.props
    this.handleUrlFlip(history, previousProps.history)
    if (
      !recommendations ||
      !previousProps.recommendations ||
      recommendations === previousProps.recommendations ||
      !currentRecommendation ||
      !previousProps.currentRecommendation ||
      currentRecommendation.index === previousProps.currentRecommendation.index
    ) {
      // this.handleRefreshedData()
    }
  }

  componentWillUnmount() {
    Logger.log('Deck ---> componentWillUnmount')
    const { dispatch } = this.props
    dispatch(unFlip())
    if (this.readTimeout) clearTimeout(this.readTimeout)
    if (this.noDataTimeout) clearTimeout(this.noDataTimeout)
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
      this.handleUnFlip()
    } else if (data.y < -height * verticalSlideRatio) {
      this.handleFlip()
    } else if (offset > horizontalSlideRatio) {
      this.handleGoPrevious()
    } else if (-offset > horizontalSlideRatio) {
      this.handleGoNext()
    }
  }

  handleGoNext = () => {
    const { history, isFlipped, nextRecommendation } = this.props
    if (!nextRecommendation || isFlipped) return
    const { offerId, mediationId } = nextRecommendation
    this.handleReadRecommendation()
    history.push(`/decouverte/${offerId || 'tuto'}/${mediationId || ''}`)
    this.handleRefreshNext()
  }

  handleGoPrevious = () => {
    const { history, isFlipped, previousRecommendation } = this.props
    if (!previousRecommendation || isFlipped) return
    const { offerId, mediationId } = previousRecommendation
    history.push(`/decouverte/${offerId || 'tuto'}/${mediationId || ''}`)
    this.handleRefreshPrevious()
  }

  handleReadRecommendation = () => {
    const { currentRecommendation, dispatch } = this.props
    const readRecommendation = Object.assign({}, currentRecommendation, {
      dateRead: moment.utc().toISOString(),
    })
    dispatch(mergeData({ readRecommendations: [readRecommendation] }))
  }

  handleRefreshPrevious = () => {
    const { currentRecommendation, previousLimit } = this.props
    if (currentRecommendation.index <= previousLimit) {
      // TODO replace by a requestData
      /*
      worker.postMessage({
        key: 'dexie-push-pull',
        state: { around: currentRecommendation.id },
      })
      */
    }
  }

  handleRefreshNext = () => {
    const { currentRecommendation, nextLimit } = this.props
    if (currentRecommendation.index >= nextLimit) {
      // TODO replace by a requestData
      /*
      worker.postMessage({
        key: 'dexie-push-pull',
        state: { around: currentRecommendation.id },
      })
      */
    }
  }

  handleRefreshedData = () => {
    this.setState(previousState => ({
      refreshKey: previousState.refreshKey + 1,
    }))
  }

  handleFlip = () => {
    const { dispatch, isFlipDisabled } = this.props
    if (isFlipDisabled) return
    dispatch(flip())
  }

  handleUnFlip = () => {
    const { dispatch, unFlippable } = this.props
    if (unFlippable) return
    dispatch(unFlip())
  }

  handleUrlFlip = (history, previousHistory = false) => {
    const { dispatch } = this.props
    const isNewUrl =
      !previousHistory ||
      (previousHistory && history.location.key !== previousHistory.location.key)
    if (isNewUrl && history.location.search.indexOf('to=verso') > 0) {
      dispatch(flipUnflippable())
    }
  }

  renderDraggableCards() {
    const {
      currentRecommendation,
      isFlipped,
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
    const draggableBounds = (isFlipped && {}) || {
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
        axis={isFlipped ? 'none' : 'exclude'}
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
      isFlipped,
      previousRecommendation,
      unFlippable,
    } = this.props

    const showCloseButton = isFlipped && !unFlippable
    const showNavigation = !isFlipped || isFlipDisabled

    return (
      <div id="deck" className="is-clipped is-relative">
        {showCloseButton && (
          <button
            type="button"
            className="close-button"
            onClick={this.handleUnFlip}
            style={{ zIndex: 300 }}
          >
            <Icon svg="ico-close" alt="Fermer" />
          </button>
        )}
        {this.renderDraggableCards()}
        {showNavigation && (
          <DeckNavigation
            recommendation={currentRecommendation}
            flipHandler={(!isFlipDisabled && this.handleFlip) || null}
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
  previousRecommendation: null,
  verticalSlideRatio: 0.1,
}

Deck.propTypes = {
  currentRecommendation: PropTypes.object,
  dispatch: PropTypes.func.isRequired,
  draggable: PropTypes.bool.isRequired,
  height: PropTypes.number.isRequired,
  history: PropTypes.object.isRequired,
  horizontalSlideRatio: PropTypes.number,
  isFlipDisabled: PropTypes.bool.isRequired,
  isFlipped: PropTypes.bool.isRequired,
  nextLimit: PropTypes.number.isRequired,
  nextRecommendation: PropTypes.object,
  previousLimit: PropTypes.number.isRequired,
  previousRecommendation: PropTypes.object,
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

  const recommendations = recommendationsSelector(state)

  return {
    currentRecommendation,
    draggable: state.verso.draggable,
    isEmpty: get(state, 'loading.config.isEmpty'),
    isFlipDisabled:
      !currentRecommendation ||
      (typeof tutoIndex === 'number' && thumbCount === 1),
    isFlipped: state.verso.isFlipped,
    nextLimit:
      recommendations &&
      (PREVIOUS_NEXT_LIMIT >= recommendations.length - 1
        ? recommendations.length - 1
        : recommendations.length - 1 - PREVIOUS_NEXT_LIMIT),
    nextRecommendation: nextRecommendationSelector(state, offerId, mediationId),
    previousLimit:
      recommendations &&
      (PREVIOUS_NEXT_LIMIT < recommendations.length - 1
        ? PREVIOUS_NEXT_LIMIT + 1
        : 0),
    previousRecommendation: previousRecommendationSelector(
      state,
      offerId,
      mediationId
    ),
    recommendations,
    unFlippable: state.verso.unFlippable,
  }
}

const mapSizeToProps = ({ width, height }) => ({
  height,
  // NOTE -> CSS body{ max-width: 500px; }
  width: Math.min(width, 500),
})

export default compose(
  withSizes(mapSizeToProps),
  connect(mapStateToProps)
)(Deck)
