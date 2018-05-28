import classnames from 'classnames'
import get from 'lodash.get'
import moment from 'moment'
import Draggable from 'react-draggable'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import { withRouter } from 'react-router-dom'
import withSizes from 'react-sizes'

import Card from './Card'
import Clue from './Clue'
import Icon from './layout/Icon'
import { requestData } from '../reducers/data'
import { flip, unFlip } from '../reducers/verso'
import selectCurrentHeaderColor from '../selectors/currentHeaderColor'
import selectCurrentRecommendation from '../selectors/currentRecommendation'
import selectIsFlipDisabled from '../selectors/isFlipDisabled'
import selectNextLimit from '../selectors/nextLimit'
import selectNextRecommendation from '../selectors/nextRecommendation'
import selectPreviousLimit from '../selectors/previousLimit'
import selectPreviousRecommendation from '../selectors/previousRecommendation'
import { IS_DEV, IS_DEXIE, ROOT_PATH } from '../utils/config'
import { getDiscoveryPath } from '../utils/routes'
import { worker } from '../workers/dexie/register'

class Deck extends Component {
  constructor() {
    super()
    this.state = {
      // isRead: false,
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

  handleNoData = () => {
    const { match: { params: { mediationId, offerId } } } = this.props
    worker.postMessage({
      key: 'dexie-push-pull',
      state: { mediationId, offerId }
    })
    this.noDataTimeout = setTimeout(() => {
      const { currentRecommendation, history } = this.props
      if (!currentRecommendation) {
        history.push('/decouverte')
      }
    }, this.props.noDataTimeout)
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

  handleSetDateRead = prevProps => {
    const {
      currentRecommendation,
      isFlipped,
      readTimeout,
      requestData
    } = this.props
    const { isRead } = this.state

    // we don't need to go further if we are still on the same reco
    if (!currentRecommendation ||
      (
        prevProps &&
        prevProps.currentRecommendation &&
        currentRecommendation &&
        prevProps.currentRecommendation.id === currentRecommendation.id)
      ) {
      return
    }

    // we need to delete the readTimeout in the case
    // where we were on a previous reco
    // and we just swipe to another before triggering the end of the readTimeout
    if (this.currentReadRecommendationId !== currentRecommendation.id) {
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
        if (
          this.props.currentRecommendation &&
          !this.props.currentRecommendation.dateRead
        ) {
          requestData('PATCH', `recommendations/${this.props.currentRecommendation.id}`,
            {
              body: {
                dateRead: moment().toISOString(),
              },
              key: 'recommendations',
              local: IS_DEXIE
            }
          )
          // this.setState({ isRead: true })
          clearTimeout(this.readTimeout)
          delete this.readTimeout
        }
      }, readTimeout)
    } else if (!isRead && currentRecommendation && currentRecommendation.dateRead) {
      // this.setState({ isRead: true })
    }
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
    this.handleNoData()
    this.handleRefreshedData()
    this.handleSetDateRead()
  }

  componentWillReceiveProps(nextProps) {
    this.handleRefreshedData(nextProps)
    this.handleDeprecatedData(nextProps)
  }

  componentDidUpdate (prevProps) {
    this.handleSetDateRead(prevProps)
  }

  componentWillUnmount () {
    this.readTimeout && clearTimeout(this.readTimeout)
    this.noDataTimeout && clearTimeout(this.noDataTimeout)
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
    const {
      // isRead,
      refreshKey
    } = this.state

    const index = get(this.props, 'currentRecommendation.index', 0)
    const position = {
      x: -1 * width * index,
      y: 0,
    }

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
            <Icon svg="ico-close" alt="Fermer" />
          </button>
        )}
        <div
          className={classnames('loading', {
            'is-invisibile': currentRecommendation,
          })}
        >
          <div>
            <Icon draggable={false} svg="ico-loading-card" alt="Chargement ..." />
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
                <Icon svg="ico-prev-w-group" alt="Précédent" />
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
                <Icon svg="ico-slideup-w" alt="Plus d'infos" />
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
                <Icon svg="ico-next-w-group" alt="Suivant" />
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
  noDataTimeout: 20000,
  readTimeout: 2000,
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
    { flip, requestData, unFlip }
  )
)(Deck)
