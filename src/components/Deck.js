import classnames from 'classnames'
import get from 'lodash.get'
import Draggable from 'react-draggable'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'

import Card from './Card'
import Clue from './Clue'
import Icon from './layout/Icon'
import { flip, unFlip } from '../reducers/verso'
import selectCurrentHeaderColor from '../selectors/currentHeaderColor'
import selectCurrentRecommendation from '../selectors/currentRecommendation'
import selectIsFlipDisabled from '../selectors/isFlipDisabled'
import selectNextLimit from '../selectors/nextLimit'
import selectNextRecommendation from '../selectors/nextRecommendation'
import selectPreviousLimit from '../selectors/previousLimit'
import selectPreviousRecommendation from '../selectors/previousRecommendation'
import { IS_DEV, ROOT_PATH } from '../utils/config'
import { getDiscoveryPath } from '../utils/routes'
import { worker } from '../workers/dexie/register'

class Deck extends Component {
  constructor() {
    super()
    this.state = {
      refreshKey: 0,
    }
  }

  handleDeprecatedData = nextProps => {
    // DEPRECATION HANDLING
    // IF THE RECO ARE DEPRECATED, WE GO TO DECOUVERTE
    const { deprecatedRecommendations } = nextProps
    if (
      deprecatedRecommendations &&
      deprecatedRecommendations !== this.props.deprecatedRecommendations
    ) {
      nextProps.history.push('/decouverte')
    }
  }

  handleGoNext = () => {
    const { history, isFlipped, nextRecommendation } = this.props
    if (!nextRecommendation || isFlipped) return
    history.push(
      getDiscoveryPath(nextRecommendation.offer, nextRecommendation.mediation)
    )
    this.handleRefreshNext()
  }

  handleGoPrevious = () => {
    const { history, isFlipped, previousRecommendation } = this.props
    if (!previousRecommendation || isFlipped) return
    history.push(
      getDiscoveryPath(
        previousRecommendation.offer,
        previousRecommendation.mediation
      )
    )
    this.handleRefreshPrevious()
  }

  handleRefreshPrevious = () => {
    const { currentRecommendation, previousLimit } = this.props
    if (currentRecommendation.index <= previousLimit) {
      worker.postMessage({
        key: 'dexie-push-pull',
        state: { around: currentRecommendation.id },
      })
    }
  }

  handleRefreshNext = () => {
    const { currentRecommendation, nextLimit } = this.props
    if (currentRecommendation.index >= nextLimit) {
      worker.postMessage({
        key: 'dexie-push-pull',
        state: { around: currentRecommendation.id },
      })
    }
  }

  handleRefreshedData = nextProps => {
    // REFRESH HANDLING
    // (ie kill the transition the short time we change the blob)
    // WE CHANGE THE KEY OF THE DRAGGABLE
    // TO FORCE IT TO REMOUNT AGAIN
    if (
      nextProps &&
      (!nextProps.recommendations ||
        !this.props.recommendations ||
        nextProps.recommendations === this.props.recommendations ||
        (!nextProps.currentRecommendation ||
          !this.props.currentRecommendation) ||
        nextProps.currentRecommendation.index ===
          this.props.currentRecommendation.index)
    ) {
      return
    }
    this.setState({ refreshKey: this.state.refreshKey + 1 })
  }

  handleFlip = () => {
    if (this.props.isFlipDisabled) return
    this.props.flip()
  }

  handleUnFlip = () => {
    if (this.props.unFlippable) return
    this.props.unFlip()
  }

  onStop = (e, data) => {
    const {
      draggable,
      horizontalSlideRatio,
      verticalSlideRatio,
      height,
      width,
    } = this.props
    const index = get(this.props, 'currentRecommendation.index', 0)
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

  componentDidMount() {
    this.handleRefreshedData()
  }

  componentWillReceiveProps(nextProps) {
    this.handleRefreshedData(nextProps)
    this.handleDeprecatedData(nextProps)
  }

  render() {
    const {
      currentHeaderColor,
      currentRecommendation,
      isFlipDisabled,
      isFlipped,
      nextRecommendation,
      previousRecommendation,
      unFlippable,
      headerColor,
      width,
    } = this.props
    const { refreshKey } = this.state

    const index = get(this.props, 'currentRecommendation.index', 0)
    const position = {
      x: -1 * width * index,
      y: 0,
    }
    console.log('currentRecommendation', currentRecommendation)
    return (
      <div
        className="deck"
        id="deck"
        style={{
          backgroundColor: headerColor,
        }}
      >
        {!unFlippable && (
          <button
            className={classnames('close-button', {
              'is-hidden': !isFlipped,
            })}
            onClick={this.handleUnFlip}
          >
            <Icon svg="ico-close" />
          </button>
        )}
        <div
          className={classnames('loading', {
            'is-invisibile': currentRecommendation,
          })}
        >
          <div>
            <Icon draggable={false} svg="ico-loading-card" />
            <h2 className="subtitle is-2">chargement des offres</h2>
          </div>
        </div>
        <Draggable
          axis={isFlipped ? 'none' : 'exclude'}
          speed={{x: 5}}
          key={refreshKey}
          position={position}
          onStop={this.onStop}
          bounds={isFlipped ? {} : { bottom: 0, top: -100, left: position.x - width, right: position.x + width }}
          enableUserSelectHack={false}
        >
          <div>
            {previousRecommendation && (
              <Card
                position="previous"
                recommendation={previousRecommendation}
              />
            )}
            <Card position="current" recommendation={currentRecommendation} />
            {nextRecommendation && (
              <Card position="next" recommendation={nextRecommendation} />
            )}
          </div>
        </Draggable>
        <div
          className={classnames('board-wrapper', { 'is-invisible': isFlipped })}
        >
          <div
            className="board-bg"
            style={{
              background: `linear-gradient(to bottom, rgba(0,0,0,0) 0%,${currentHeaderColor} 30%,${currentHeaderColor} 100%)`,
            }}
          />
          <ul
            className={classnames('controls', {
              'is-invisible': isFlipped,
            })}
            style={{ backgroundImage: `url('${ROOT_PATH}/mosaic-w@2x.png')` }}
          >
            <li>
              <button
                className={classnames('button before', {
                  'is-invisible': !previousRecommendation,
                })}
                onClick={this.handleGoPrevious}
              >
                <Icon svg="ico-prev-w-group" />
              </button>
            </li>
            <li>
              <button
                className={classnames('button to-recto', {
                  'is-invisible': isFlipDisabled,
                })}
                disabled={isFlipDisabled}
                onClick={this.handleFlip}
              >
                <Icon svg="ico-slideup-w" />
              </button>
              <Clue />
            </li>
            <li>
              <button
                className={classnames('button after', {
                  'is-invisible': !nextRecommendation,
                })}
                onClick={this.handleGoNext}
              >
                <Icon svg="ico-next-w-group" />
              </button>
            </li>
          </ul>
        </div>
        {IS_DEV && (
          <div className="debug debug-deck">
            ({this.props.isLoadingBefore ? '?' : ' '}
            {this.props.previousLimit}){' '}
            {this.props.currentRecommendation &&
              this.props.currentRecommendation.index}{' '}
            ({this.props.nextLimit} {this.props.isLoadingAfter ? '?' : ' '}) /{' '}
            {this.props.recommendations &&
              this.props.recommendations.length - 1}
          </div>
        )}
      </div>
    )
  }
}

Deck.defaultProps = {
  flipRatio: 0.25,
  horizontalSlideRatio: 0.2,
  verticalSlideRatio: 0.1,
  isDebug: false,
  readTimeout: 3000,
  resizeTimeout: 250,
  transitionTimeout: 500,
}

export default compose(
  withRouter,
  withSizes(({ width, height }) => ({
    width: Math.min(width, 500), // body{max-width: 500px;}
    height,
  })),
  connect(
    state => ({
      currentHeaderColor: selectCurrentHeaderColor(state),
      currentRecommendation: selectCurrentRecommendation(state),
      deprecatedRecommendations: state.data.deprecatedRecommendations,
      isFlipDisabled: selectIsFlipDisabled(state),
      isFlipped: state.verso.isFlipped,
      nextLimit: selectNextLimit(state),
      nextRecommendation: selectNextRecommendation(state),
      previousLimit: selectPreviousLimit(state),
      previousRecommendation: selectPreviousRecommendation(state),
      recommendations: state.data.recommendations,
      unFlippable: state.verso.unFlippable,
      draggable: state.verso.draggable,
    }),
    { flip, unFlip }
  )
)(Deck)
