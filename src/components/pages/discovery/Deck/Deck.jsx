import get from 'lodash.get'
import PropTypes from 'prop-types'
import React, { Component } from 'react'
import Draggable from 'react-draggable'

import CardContainer from './Card/CardContainer'
import NavigationContainer from './Navigation/NavigationContainer'
import CloseLink from '../../../layout/Header/CloseLink/CloseLink'
import getAreDetailsVisible from '../../../../helpers/getAreDetailsVisible'
import getUrlWithoutDetailsPart from '../../../../helpers/getUrlWithoutDetailsPart'
import getIsTransitionDetailsUrl from '../../../../helpers/getIsTransitionDetailsUrl'

class Deck extends Component {
  constructor(props) {
    super(props)
    this.state = {
      refreshKey: 0,
    }
  }

  componentDidMount() {
    const { currentRecommendation, recommendations } = this.props
    const isStateWithoutRecommendationsOrCurrentRecommendation =
      !recommendations || recommendations.length === 0 || !currentRecommendation

    if (!isStateWithoutRecommendationsOrCurrentRecommendation) return
    this.handleRefreshedDraggableKey()
  }

  componentDidUpdate() {
    const { history, location, match } = this.props
    const isTransitionDetailsUrl = getIsTransitionDetailsUrl(match)

    if (isTransitionDetailsUrl) {
      const { pathname, search } = location
      const nextUrl = `${pathname.split('/transition')[0]}${search}`
      history.replace(nextUrl)
    }
  }

  componentWillUnmount() {
    const { readTimeout, noDataTimeout } = this.props

    if (readTimeout) clearTimeout(readTimeout)
    if (noDataTimeout) clearTimeout(noDataTimeout)
  }

  handleOnStop = (event, data) => {
    const {
      currentRecommendation,
      height,
      horizontalSlideRatio,
      verticalSlideRatio,
      width,
    } = this.props

    const index = get(currentRecommendation, 'index', 0)
    const offset = (data.x + width * index) / width
    if (data.y > height * verticalSlideRatio) {
      this.onHandleCloseCardDetails()
    } else if (data.y < -height * verticalSlideRatio) {
      this.handleShowCardDetails()
    } else if (offset > horizontalSlideRatio) {
      this.handleGoPrevious()
    } else if (-offset > horizontalSlideRatio) {
      this.handleGoNext()
    }
  }

  handleGoNext = () => {
    const { history, match, nextRecommendation } = this.props
    const areDetailsVisible = getAreDetailsVisible(match)
    if (!nextRecommendation || areDetailsVisible) return
    const { offerId, mediationId } = nextRecommendation
    const nextUrl = `/decouverte/${offerId || 'tuto'}${`/${mediationId || 'vide'}`}`
    history.push(nextUrl)
    this.handleRefreshNext()
  }

  handleGoPrevious = () => {
    const { history, match, previousRecommendation } = this.props
    const areDetailsVisible = getAreDetailsVisible(match)
    if (!previousRecommendation || areDetailsVisible) return
    const { offerId, mediationId } = previousRecommendation
    const previousUrl = `/decouverte/${offerId || 'tuto'}${`/${mediationId || 'vide'}`}`
    history.push(previousUrl)
  }

  handleRefreshNext = () => {
    const { currentRecommendation, handleRequestPutRecommendations, nextLimit } = this.props
    const shouldRequest = nextLimit && currentRecommendation.index === nextLimit
    if (!shouldRequest) return
    handleRequestPutRecommendations()
  }

  handleRefreshedDraggableKey = () => {
    this.setState(previousState => ({
      refreshKey: previousState.refreshKey + 1,
    }))
  }

  handleShowCardDetails = () => {
    const { isFlipDisabled, history, location, match } = this.props
    const { pathname, search } = location
    const areDetailsVisible = getAreDetailsVisible(match)
    if (areDetailsVisible || isFlipDisabled) return
    const detailsUrl = `${pathname}/details${search}`
    history.push(detailsUrl)
  }

  onHandleCloseCardDetails = () => {
    const { history, location, match } = this.props
    const removedDetailsUrl = getUrlWithoutDetailsPart(location, match)

    if (removedDetailsUrl) {
      history.push(removedDetailsUrl)
    }
  }

  buildCloseToUrl = () => {
    const { location, match } = this.props
    return getUrlWithoutDetailsPart(location, match) + '/transition'
  }

  renderDraggableCards() {
    const {
      currentRecommendation,
      match,
      nextRecommendation,
      previousRecommendation,
      width,
    } = this.props
    const { index } = currentRecommendation || {}
    const { refreshKey } = this.state
    const areDetailsVisible = getAreDetailsVisible(match)

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
        axis={areDetailsVisible ? 'none' : 'exclude'}
        bounds={draggableBounds}
        enableUserSelectHack={false}
        key={refreshKey}
        onStop={this.handleOnStop}
        position={position}
        speed={{ x: 5 }}
      >
        <div className="is-overlay">
          <div className="inner is-relative">
            {previousRecommendation && <CardContainer position="previous" />}
            <CardContainer position="current" />
            {nextRecommendation && <CardContainer position="next" />}
          </div>
        </div>
      </Draggable>
    )
  }

  render() {
    const {
      currentRecommendation,
      height,
      isFlipDisabled,
      match,
      nextRecommendation,
      previousRecommendation,
      recommendations,
    } = this.props
    const areDetailsVisible = getAreDetailsVisible(match)
    const showNavigation = !areDetailsVisible || isFlipDisabled

    return (
      <div
        className="is-clipped is-relative"
        data-nb-recos={recommendations.length}
        id="deck"
      >
        {areDetailsVisible && <CloseLink
          closeTitle="Fermer"
          closeTo={this.buildCloseToUrl()}
                              />}
        {this.renderDraggableCards()}
        {showNavigation && currentRecommendation && (
          <NavigationContainer
            flipHandler={(!isFlipDisabled && this.handleShowCardDetails) || null}
            handleGoNext={(nextRecommendation && this.handleGoNext) || null}
            handleGoPrevious={(previousRecommendation && this.handleGoPrevious) || null}
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
  currentRecommendation: PropTypes.shape(),
  handleRequestPutRecommendations: PropTypes.func.isRequired,
  height: PropTypes.number.isRequired,
  history: PropTypes.shape({
    push: PropTypes.func.isRequired,
    replace: PropTypes.func.isRequired,
  }).isRequired,
  horizontalSlideRatio: PropTypes.number,
  isFlipDisabled: PropTypes.bool.isRequired,
  location: PropTypes.shape({
    pathname: PropTypes.string.isRequired,
    search: PropTypes.string.isRequired,
  }).isRequired,
  match: PropTypes.shape({
    params: PropTypes.shape({
      details: PropTypes.string,
    }).isRequired,
  }).isRequired,
  nextLimit: PropTypes.oneOfType([PropTypes.bool, PropTypes.number]).isRequired,
  nextRecommendation: PropTypes.shape(),
  noDataTimeout: PropTypes.number,
  previousRecommendation: PropTypes.shape(),
  readTimeout: PropTypes.number,
  recommendations: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  verticalSlideRatio: PropTypes.number,
  width: PropTypes.number.isRequired,
}

export default Deck
