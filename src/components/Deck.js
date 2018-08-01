import get from 'lodash.get'
import moment from 'moment'
import { requestData as requestDataAction } from 'pass-culture-shared'
import Draggable from 'react-draggable'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'
import PropTypes from 'prop-types'

import Card from './Card'
import DeckDebugger from './layout/DeckDebugger'
import DeckNavigation from './layout/DeckNavigation'
import Icon from './layout/Icon'
import { flip as flipAction, unFlip as unFlipAction } from '../reducers/verso'
import currentRecommendationSelector from '../selectors/currentRecommendation'
import isFlipDisabledSelector from '../selectors/isFlipDisabled'
import nextLimitSelector from '../selectors/nextLimit'
import nextRecommendationSelector from '../selectors/nextRecommendation'
import previousLimitSelector from '../selectors/previousLimit'
import previousRecommendationSelector from '../selectors/previousRecommendation'
import { IS_DEV } from '../utils/config'

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
    const {
      currentRecommendation,
      recommendations
    } = this.props
    if (!recommendations || !currentRecommendation) {
      // this.handleRefreshedData()
    }
    // this.handleSetDateRead()
  }

  componentDidUpdate (previousProps) {
    const {
      currentRecommendation,
      recommendations
    } = this.props
    if (
      (!recommendations ||
        !previousProps.recommendations ||
        recommendations === previousProps.recommendations ||
        !currentRecommendation ||
        !previousProps.currentRecommendation) ||
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

  handleDeprecatedData = nextProps => {
    // DEPRECATION HANDLING
    // IF THE RECO ARE DEPRECATED, WE GO TO DECOUVERTE
    const { deprecatedRecommendations: nextDeprecated } = nextProps
    const { deprecatedRecommendations: currDeprecated } = this.props
    if (nextDeprecated && nextDeprecated !== currDeprecated) {
      // nextProps.history.push('/decouverte')
    }
  }

  handleGoNext = () => {
    const { history, isFlipped, nextRecommendation } = this.props
    if (!nextRecommendation || isFlipped) return
    history.push(nextRecommendation.path)
  }

  handleGoPrevious = () => {
    const { history, isFlipped, previousRecommendation } = this.props
    if (!previousRecommendation || isFlipped) return
    history.push(previousRecommendation.path)
  }

  handleRefreshedData = () => {
    this.setState(previousState =>
      ({ refreshKey: previousState.refreshKey + 1 }))
  }

  handleSetDateRead(prevProps) {
    const {
      isFlipped,
      readTimeout,
      requestData,
      currentRecommendation,
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
          requestData('PATCH', `recommendations/${currentRecommendation.id}`, {
            body: {
              dateRead: moment().toISOString(),
            },
          })
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
    const { isFlipDisabled, flip } = this.props
    if (isFlipDisabled) return
    flip()
  }

  handleUnFlip() {
    const { unFlippable, unFlip } = this.props
    if (unFlippable) return
    unFlip()
  }

  renderDraggableCards() {
    const {
      currentRecommendation,
      draggable,
      height,
      horizontalSlideRatio,
      isFlipped,
      nextRecommendation,
      previousRecommendation,
      verticalSlideRatio,
      width,
    } = this.props
    const {
      index
    } = (currentRecommendation || {})
    const { refreshKey } = this.state

    const position = {
      x: -1 * width * index,
      y: 0,
    }
    const draggableBounds = (isFlipped && {}) || {
      top: -100,
      bottom: 0,
      left: position.x - width,
      right: position.x + width,
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
          {previousRecommendation && (
            <Card position="previous" />
          )}
          <Card position="current" />
          {nextRecommendation && (
            <Card position="next" />
          )}
        </div>
      </Draggable>
    )
  }

  render() {
    const {
      currentHeaderColor,
      currentRecommendation,
      nextRecommendation,
      isEmpty,
      isFlipDisabled,
      isFlipped,
      previousRecommendation,
      unFlippable,
      width,
    } = this.props
    const {
      index
    } = (currentRecommendation || 0)

    const showLoader = !currentRecommendation
    const showCloseButton = isFlipped && !unFlippable
    const showNavigation = !isFlipped || isFlipDisabled

    const position = {
      x: -1 * width * index,
      y: 0,
    }

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
            currentHeaderColor={currentHeaderColor}
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
  // flipRatio: 0.25,
  isEmpty: false,
  horizontalSlideRatio: 0.2,
  verticalSlideRatio: 0.1,
  // isDebug: false,
  // noDataTimeout: 20000,
  readTimeout: 2000,
  // resizeTimeout: 250,
  // transitionTimeout: 500,
  nextRecommendation: null,
  currentRecommendation: null,
  previousRecommendation: null,
  deprecatedRecommendations: null,
}

Deck.propTypes = {
  // isDebug: PropTypes.bool,
  // resizeTimeout: PropTypes.number,
  // transitionTimeout: PropTypes.number,
  // noDataTimeout: PropTypes.number,
  isEmpty: PropTypes.bool,
  height: PropTypes.number.isRequired,
  width: PropTypes.number.isRequired,
  flip: PropTypes.func.isRequired,
  unFlip: PropTypes.func.isRequired,
  draggable: PropTypes.bool.isRequired,
  requestData: PropTypes.func.isRequired,
  // flipRatio: PropTypes.number,
  verticalSlideRatio: PropTypes.number,
  readTimeout: PropTypes.number,
  horizontalSlideRatio: PropTypes.number,
  isFlipDisabled: PropTypes.bool.isRequired,
  unFlippable: PropTypes.bool.isRequired,
  history: PropTypes.object.isRequired,
  isFlipped: PropTypes.bool.isRequired,
  currentRecommendation: PropTypes.object,
  recommendations: PropTypes.array.isRequired,
  currentHeaderColor: PropTypes.string.isRequired,
  nextRecommendation: PropTypes.object,
  deprecatedRecommendations: PropTypes.object,
  previousRecommendation: PropTypes.object,
}

const mapStateToProps = (state, ownProps) => {
  const { mediationId, offerId } = ownProps.match.params
  return {
    currentRecommendation: currentRecommendationSelector(state,
      offerId, mediationId),
    isEmpty: get(state, 'loading.config.isEmpty'),
    isFlipDisabled: isFlipDisabledSelector(state, offerId, mediationId),
    isFlipped: state.verso.isFlipped,
    nextLimit: nextLimitSelector(state),
    nextRecommendation: nextRecommendationSelector(state, offerId, mediationId),
    previousLimit: previousLimitSelector(state),
    previousRecommendation: previousRecommendationSelector(state, offerId, mediationId),
    recommendations: state.data.recommendations || [],
    unFlippable: state.verso.unFlippable,
    draggable: state.verso.draggable,
  }
}

const mapSizeToProps = ({ width, height }) => ({
  // body{max-width: 500px;}
  width: Math.min(width, 500),
  height,
})

const mapDispatchToProps = {
  flip: flipAction,
  requestData: requestDataAction,
  unFlip: unFlipAction
}

export default compose(
  withRouter,
  withSizes(mapSizeToProps),
  connect(mapStateToProps, mapDispatchToProps)
)(Deck)
