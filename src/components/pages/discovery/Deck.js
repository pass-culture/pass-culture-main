import get from 'lodash.get'
import { Logger, Icon } from 'pass-culture-shared'
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

export class RawDeck extends Component {
  constructor(props) {
    super(props)
    this.currentReadRecommendationId = null
    this.state = { refreshKey: 0 }
  }

  componentDidMount() {
    Logger.log('DECK ---> componentDidMount')
    console.log('DECK ---> componentDidMount')
    const { currentRecommendation, history, recommendations } = this.props
    this.handleUrlFlip(history)
    console.log(
      'DECK ---> componentDidMount : currentRecommendation',
      currentRecommendation
    )
    console.log('DECK ---> componentDidMount : history', history)
    if (!recommendations || !currentRecommendation) {
      this.handleRefreshedData()
    }
  }

  componentDidUpdate(previousProps) {
    Logger.log('DECK ---> componentDidUpdate', previousProps)
    console.log('**** DECK ---> componentDidUpdate')
    const { currentRecommendation, history, recommendations } = this.props
    console.log('history', history)
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
    Logger.log('DECK ---> componentWillUnmount')
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
    console.log("Adieu l'ami, salut le trésor !")
    // this.setState(previousState => ({
    //   refreshKey: previousState.refreshKey + 1,
    // }))
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
    console.log('°°°°°°° handleUrlFlip history : °°°°°°°°', history)
    // console.log(
    //   'history.location ',
    //   history.location.search.indexOf('to=verso')
    // )
    console.log('previousHistory : ', previousHistory)
    Logger.log('DECK ---> handleUrlFlip')
    const { dispatch } = this.props
    const isNewUrl =
      !previousHistory ||
      (previousHistory && history.location.key !== previousHistory.location.key)
    if (isNewUrl && history.location.search.indexOf('to=verso') > 0) {
      console.log(
        '*********************************************************************************************************************** DISPATCH *********************************************************************************************************************** '
      )
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

    // console.log('****** PROPS ********', this.props)

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

RawDeck.defaultProps = {
  currentRecommendation: null,
  horizontalSlideRatio: 0.2,
  nextRecommendation: null,
  previousRecommendation: null,
  verticalSlideRatio: 0.1,
}

RawDeck.propTypes = {
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
  // console.log('^^^^^^^^^ ownProps ^^^^^^^^^', ownProps.match)
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

const Deck = compose(
  withSizes(mapSizeToProps),
  connect(mapStateToProps)
)(RawDeck)

export default Deck
