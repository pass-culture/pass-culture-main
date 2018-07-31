import classnames from 'classnames'
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
import Clue from './Clue'
import Icon from './layout/Icon'

import { flip as flipAction, unFlip as unFlipAction } from '../reducers/verso'
import selectCurrentHeaderColor from '../selectors/currentHeaderColor'
import selectCurrentRecommendation from '../selectors/currentRecommendation'
import selectIsFlipDisabled from '../selectors/isFlipDisabled'
import selectNextLimit from '../selectors/nextLimit'
import selectNextRecommendation from '../selectors/nextRecommendation'
import selectPreviousLimit from '../selectors/previousLimit'
import selectPreviousRecommendation from '../selectors/previousRecommendation'
import { IS_DEV, ROOT_PATH } from '../utils/config'
import { getDiscoveryPath } from '../utils/routes'

class Deck extends Component {
  constructor() {
    super()
    this.state = {
      // isRead: false,
      refreshKey: 0,
    }
  }

  componentDidMount() {
    this.handleRefreshedData()
    // this.handleSetDateRead()
  }

  componentWillReceiveProps(nextProps) {
    this.handleRefreshedData(nextProps)
    this.handleDeprecatedData(nextProps)
  }

  // componentDidUpdate(prevProps) {
  // this.handleSetDateRead(prevProps)
  // }

  componentWillUnmount() {
    if (this.readTimeout) clearTimeout(this.readTimeout)
    if (this.noDataTimeout) clearTimeout(this.noDataTimeout)
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

  handleFlip = () => {
    const { isFlipDisabled, flip } = this.props
    if (isFlipDisabled) return
    flip()
  }

  handleUnFlip = () => {
    const { unFlippable, unFlip } = this.props
    if (unFlippable) return
    unFlip()
  }

  handleSetDateRead = prevProps => {
    const {
      currentRecommendation,
      isFlipped,
      readTimeout,
      requestData,
    } = this.props
    const { isRead } = this.state

    // we don't need to go further if we are still on the same reco
    if (
      !currentRecommendation ||
      (prevProps &&
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
          requestData(
            'PATCH',
            `recommendations/${this.props.currentRecommendation.id}`,
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

  handleRefreshedData = nextProps => {
    const { recommendations, currentRecommendation } = this.props
    // REFRESH HANDLING
    // (ie kill the transition the short time we change the blob)
    // WE CHANGE THE KEY OF THE DRAGGABLE
    // TO FORCE IT TO REMOUNT AGAIN
    if (
      nextProps &&
      (!nextProps.recommendations ||
        !recommendations ||
        nextProps.recommendations === recommendations ||
        (!nextProps.currentRecommendation || !currentRecommendation) ||
        nextProps.currentRecommendation.index === currentRecommendation.index)
    ) {
      return
    }
    this.setState(prev => ({ refreshKey: prev.refreshKey + 1 }))
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
  }

  handleGoNext = () => {
    const { history, isFlipped, nextRecommendation } = this.props
    if (!nextRecommendation || isFlipped) return
    history.push(
      getDiscoveryPath(nextRecommendation.offer, nextRecommendation.mediation)
    )
  }

  handleDeprecatedData = nextProps => {
    // DEPRECATION HANDLING
    // IF THE RECO ARE DEPRECATED, WE GO TO DECOUVERTE
    const { deprecatedRecommendations: nextdeprecated } = nextProps
    const { deprecatedRecommendations: currdeprecated } = this.props
    if (nextdeprecated && nextdeprecated !== currdeprecated) {
      // nextProps.history.push('/decouverte')
    }
  }

  render() {
    const {
      currentHeaderColor,
      currentRecommendation,
      isEmpty,
      isFlipDisabled,
      isFlipped,
      recommendations,
      nextRecommendation,
      previousRecommendation,
      unFlippable,
      headerColor,
      previousLimit,
      isLoadingAfter,
      isLoadingBefore,
      width,
      nextLimit,
    } = this.props
    const {
      // isRead,
      refreshKey,
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
            type="button"
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
        <Draggable
          axis={isFlipped ? 'none' : 'exclude'}
          speed={{ x: 5 }}
          key={refreshKey}
          position={position}
          onStop={this.onStop}
          bounds={
            isFlipped
              ? {}
              : {
                  bottom: 0,
                  top: -100,
                  left: position.x - width,
                  right: position.x + width,
                }
          }
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
          className={classnames('board-wrapper', {
            'is-invisible': isFlipped,
          })}
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
                type="button"
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
                type="button"
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
                type="button"
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
            (
            {this.props.isLoadingBefore ? '?' : ' '}
            {this.props.previousLimit}
)
            {' '}
            {this.props.currentRecommendation &&
              this.props.currentRecommendation.mediation &&
              this.props.currentRecommendation.mediation.id}
            {' '}
            {this.props.currentRecommendation &&
              this.props.currentRecommendation.index}
            {' '}
            (
            {this.props.nextLimit} 
            {' '}
            {this.props.isLoadingAfter ? '?' : ' '}
) /
            {' '}
            {this.props.recommendations &&
              this.props.recommendations.length - 1}
          </div>
        )}
      </div>
    )
  }
}

Deck.defaultProps = {
  // flipRatio: 0.25,
  horizontalSlideRatio: 0.2,
  verticalSlideRatio: 0.1,
  // isDebug: false,
  // noDataTimeout: 20000,
  readTimeout: 2000,
  // resizeTimeout: 250,
  // transitionTimeout: 500,
  currentRecommendation: null,
}

Deck.propTypes = {
  // isDebug: PropTypes.bool,
  // resizeTimeout: PropTypes.number,
  // transitionTimeout: PropTypes.number,
  // noDataTimeout: PropTypes.number,
  height: PropTypes.func.isRequired,
  width: PropTypes.func.isRequired,
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
  isLoadingBefore: PropTypes.bool.isRequired,
  nextLimit: PropTypes.bool.isRequired,
  isLoadingAfter: PropTypes.bool.isRequired,
  previousLimit: PropTypes.bool.isRequired,
  currentRecommendation: PropTypes.object,
  recommendations: PropTypes.array.isRequired,
  headerColor: PropTypes.object.isRequired,
  currentHeaderColor: PropTypes.object.isRequired,
  nextRecommendation: PropTypes.object.isRequired,
  deprecatedRecommendations: PropTypes.object.isRequired,
  previousRecommendation: PropTypes.object.isRequired,
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
      isEmpty: get(state, 'loading.config.isEmpty'),
      isFlipDisabled: selectIsFlipDisabled(state),
      isFlipped: state.verso.isFlipped,
      nextLimit: selectNextLimit(state),
      nextRecommendation: selectNextRecommendation(state),
      previousLimit: selectPreviousLimit(state),
      previousRecommendation: selectPreviousRecommendation(state),
      recommendations: state.data.recommendations || [],
      unFlippable: state.verso.unFlippable,
      draggable: state.verso.draggable,
    }),
    { flip: flipAction, requestData: requestDataAction, unFlip: unFlipAction }
  )
)(Deck)
