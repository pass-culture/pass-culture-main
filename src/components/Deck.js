import get from 'lodash.get'
import moment from 'moment'
import { Icon, requestData } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import Draggable from 'react-draggable'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'

import Card from './Card'
import DeckDebugger from './DeckDebugger'
import DeckNavigation from './DeckNavigation'
import { flip, unFlip } from '../reducers/verso'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import nextRecommendationSelector from '../selectors/nextRecommendation'
import previousRecommendationSelector from '../selectors/previousRecommendation'
import recommendationsSelector from '../selectors/recommendations'
import { IS_DEV } from '../utils/config'
import { PREVIOUS_NEXT_LIMIT } from '../utils/deck'

class Deck extends Component {
  constructor(props) {
    super(props)
    this.currentReadRecommendationId = null
    this.state = { refreshKey: 0 }
    this.onStop = this.onStop.bind(this)
    this.handleFlip = this.handleFlip.bind(this)
    this.handleGoNext = this.handleGoNext.bind(this)
    this.handleUnFlip = this.handleUnFlip.bind(this)
    this.handleGoPrevious = this.handleGoPrevious.bind(this)
    this.handleSetDateRead = this.handleSetDateRead.bind(this)
    this.handleRefreshedData = this.handleRefreshedData.bind(this)
  }

  componentDidMount() {
    const { currentRecommendation, recommendations } = this.props
    if (!recommendations || !currentRecommendation) {
      // this.handleRefreshedData()
    }
    // this.handleSetDateRead()
  }

  componentDidUpdate(previousProps) {
    const { currentRecommendation, recommendations } = this.props
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
    if (this.readTimeout) clearTimeout(this.readTimeout)
    if (this.noDataTimeout) clearTimeout(this.noDataTimeout)
  }

  onStop(e, data) {
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

  handleSetDateRead(prevProps) {
    const {
      currentRecommendation,
      dispatchRequestData,
      isFlipped,
      readTimeout,
    } = this.props
    const { isRead } = this.state

    const isSameReco =
      !currentRecommendation ||
      (prevProps &&
        prevProps.currentRecommendation &&
        currentRecommendation &&
        prevProps.currentRecommendation.id === currentRecommendation.id)
    // we don't need to go further if we are still on the same reco
    if (isSameReco) return

    const isCurrentReco =
      this.currentReadRecommendationId !== currentRecommendation.id
    // we need to delete the readTimeout in the case
    // where we were on a previous reco
    // and we just swipe to another before triggering the end of the readTimeout
    if (isCurrentReco) {
      clearTimeout(this.readTimeout)
      delete this.readTimeout
    }

    // if the reco is not read yet
    // we trigger a timeout in the end of which
    // we will request a dateRead Patch if we are still
    // on the same reco
    if (!this.readTimeout && !isFlipped && !currentRecommendation.dateRead) {
      // this.setState({ isRead: false })
      this.currentReadRecommendationId = currentRecommendation.id
      this.readTimeout = setTimeout(() => {
        if (currentRecommendation && !currentRecommendation.dateRead) {
          dispatchRequestData(
            'PATCH',
            `recommendations/${currentRecommendation.id}`,
            {
              body: {
                dateRead: moment().toISOString(),
              },
            }
          )
          // this.setState({ isRead: true })
          clearTimeout(this.readTimeout)
          delete this.readTimeout
        }
      }, readTimeout)
    } else if (
      !isRead &&
      currentRecommendation &&
      currentRecommendation.dateRead
    ) {
      // this.setState({ isRead: true })
    }
  }

  handleFlip() {
    const { dispatchFlip, isFlipDisabled } = this.props
    if (isFlipDisabled) return
    dispatchFlip()
  }

  handleUnFlip() {
    const { dispatchUnFlip, unFlippable } = this.props
    if (unFlippable) return
    dispatchUnFlip()
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
        <div>
          {previousRecommendation && <Card position="previous" />}
          <Card position="current" />
          {nextRecommendation && <Card position="next" />}
        </div>
      </Draggable>
    )
  }

  render() {
    const {
      currentRecommendation,
      nextRecommendation,
      isEmpty,
      isFlipDisabled,
      isFlipped,
      previousRecommendation,
      unFlippable,
    } = this.props

    const showLoader = !currentRecommendation
    const showCloseButton = isFlipped && !unFlippable
    const showNavigation = !isFlipped || isFlipDisabled

    return (
      <div className="deck" id="deck">
        {showLoader && (
          <div className="loading">
            <div>
              <Icon
                draggable={false}
                svg="ico-loading-card"
                alt="Chargement ..."
              />
              <h2 className="subtitle is-2">
                {isEmpty
                  ? 'aucune offre pour le moment'
                  : 'chargement des offres'}
              </h2>
            </div>
          </div>
        )}
        {showCloseButton && (
          <button
            type="button"
            className="close-button"
            onClick={this.handleUnFlip}
          >
            <Icon svg="ico-close" alt="Fermer" />
          </button>
        )}
        {this.renderDraggableCards()}
        {showNavigation && (
          <DeckNavigation
            flipHandler={(!isFlipDisabled && this.handleFlip) || null}
            handleGoNext={(nextRecommendation && this.handleGoNext) || null}
            handleGoPrevious={
              (previousRecommendation && this.handleGoPrevious) || null
            }
          />
        )}
        {IS_DEV && (
          <DeckDebugger currentRecommendation={currentRecommendation} />
        )}
      </div>
    )
  }
}

Deck.defaultProps = {
  currentRecommendation: null,
  // flipRatio: 0.25,
  horizontalSlideRatio: 0.2,
  isEmpty: false,
  nextRecommendation: null,
  previousRecommendation: null,
  readTimeout: 2000,
  verticalSlideRatio: 0.1,
  // noDataTimeout: 20000,
}

Deck.propTypes = {
  currentRecommendation: PropTypes.object,
  dispatchFlip: PropTypes.func.isRequired,
  dispatchRequestData: PropTypes.func.isRequired,
  dispatchUnFlip: PropTypes.func.isRequired,
  draggable: PropTypes.bool.isRequired,
  height: PropTypes.number.isRequired,
  history: PropTypes.object.isRequired,
  horizontalSlideRatio: PropTypes.number,
  isEmpty: PropTypes.bool,
  isFlipDisabled: PropTypes.bool.isRequired,
  isFlipped: PropTypes.bool.isRequired,
  nextLimit: PropTypes.number.isRequired,
  nextRecommendation: PropTypes.object,
  previousLimit: PropTypes.number.isRequired,
  previousRecommendation: PropTypes.object,
  // flipRatio: PropTypes.number,
  // isDebug: PropTypes.bool,
  // noDataTimeout: PropTypes.number,
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
  // body{max-width: 500px;}
  height,
  width: Math.min(width, 500),
})

const mapDispatchToProps = {
  dispatchFlip: flip,
  dispatchRequestData: requestData,
  dispatchUnFlip: unFlip,
}

export default compose(
  withRouter,
  withSizes(mapSizeToProps),
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Deck)
