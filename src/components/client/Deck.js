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
import Icon from '../layout/Icon'
import { flip, unFlip } from '../../reducers/verso'
import selectCurrentHeaderColor from '../../selectors/currentHeaderColor'
import selectCurrentUserMediation from '../../selectors/currentUserMediation'
import selectIsFlipDisabled from '../../selectors/isFlipDisabled'
import selectNextLimit from '../../selectors/nextLimit'
import selectNextUserMediation from '../../selectors/nextUserMediation'
import selectPreviousLimit from '../../selectors/previousLimit'
import selectPreviousUserMediation from '../../selectors/previousUserMediation'
import { IS_DEV, ROOT_PATH } from '../../utils/config'
import { getDiscoveryPath } from '../../utils/routes'
import { worker } from '../../workers/dexie/register'

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
    const { deprecatedUserMediations } = nextProps
    if (
      deprecatedUserMediations &&
      deprecatedUserMediations !== this.props.deprecatedUserMediations
    ) {
      nextProps.history.push('/decouverte')
    }
  }

  handleGoNext = () => {
    const { history, isFlipped, nextUserMediation } = this.props
    if (!nextUserMediation || isFlipped) return
    history.push(
      getDiscoveryPath(nextUserMediation.offer, nextUserMediation.mediation)
    )
    this.handleRefreshNext()
  }

  handleGoPrevious = () => {
    const { history, isFlipped, previousUserMediation } = this.props
    if (!previousUserMediation || isFlipped) return
    history.push(
      getDiscoveryPath(
        previousUserMediation.offer,
        previousUserMediation.mediation
      )
    )
    this.handleRefreshPrevious()
  }

  handleRefreshPrevious = () => {
    const { currentUserMediation, previousLimit } = this.props
    if (currentUserMediation.index <= previousLimit) {
      worker.postMessage({
        key: 'dexie-push-pull',
        state: { around: currentUserMediation.id },
      })
    }
  }

  handleRefreshNext = () => {
    const { currentUserMediation, nextLimit } = this.props
    if (currentUserMediation.index >= nextLimit) {
      worker.postMessage({
        key: 'dexie-push-pull',
        state: { around: currentUserMediation.id },
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
      (!nextProps.userMediations ||
        !this.props.userMediations ||
        nextProps.userMediations === this.props.userMediations ||
        (!nextProps.currentUserMediation || !this.props.currentUserMediation) ||
        nextProps.currentUserMediation.index ===
          this.props.currentUserMediation.index)
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
      horizontalSlideRatio,
      verticalSlideRatio,
      height,
      width,
    } = this.props
    const index = get(this.props, 'currentUserMediation.index', 0)
    const offset = (data.x + width * index) / width
    if (offset > horizontalSlideRatio) {
      this.handleGoPrevious()
    } else if (-offset > horizontalSlideRatio) {
      this.handleGoNext()
    } else if (data.y > height * verticalSlideRatio) {
      this.handleUnFlip()
    } else if (data.y < -height * verticalSlideRatio) {
      this.handleFlip()
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
      currentUserMediation,
      isFlipDisabled,
      isFlipped,
      nextUserMediation,
      previousUserMediation,
      unFlippable,
      headerColor,
      width,
    } = this.props
    const { refreshKey } = this.state

    const index = get(this.props, 'currentUserMediation.index', 0)
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
            className={classnames('button close', {
              hidden: !isFlipped,
            })}
            onClick={this.handleUnFlip}
          >
            <Icon svg="ico-close" />
          </button>
        )}
        <div
          className={classnames('loading flex items-center justify-center', {
            shown: !currentUserMediation,
          })}
        >
          <div>
            <Icon draggable={false} svg="ico-loading-card" />
            <div className="h2">chargement des offres</div>
          </div>
        </div>
        <Draggable
          axis={isFlipped ? 'none' : 'exclude'}
          key={refreshKey}
          position={position}
          onStop={this.onStop}
          bounds={isFlipped ? {} : { bottom: 0, top: -100 }}
          enableUserSelectHack={false}
        >
          <div>
            {previousUserMediation && (
              <Card position="previous" userMediation={previousUserMediation} />
            )}
            <Card position="current" userMediation={currentUserMediation} />
            {nextUserMediation && (
              <Card position="next" userMediation={nextUserMediation} />
            )}
          </div>
        </Draggable>
        <div className={classnames('board-wrapper', { hidden: isFlipped })}>
          <div
            className="board-bg"
            style={{
              background: `linear-gradient(to bottom, rgba(0,0,0,0) 0%,${currentHeaderColor} 30%,${currentHeaderColor} 100%)`,
            }}
          />
          <ul
            className={classnames('controls', {
              hidden: isFlipped,
            })}
            style={{ backgroundImage: `url('${ROOT_PATH}/mosaic-w@2x.png')` }}
          >
            <li>
              <button
                className={classnames('button before', {
                  hidden: !previousUserMediation,
                })}
                onClick={this.handleGoPrevious}
              >
                <Icon svg="ico-prev-w-group" />
              </button>
            </li>
            <li>
              <button
                className={classnames('button to-recto', {
                  hidden: isFlipDisabled,
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
                className={classnames('after button', {
                  hidden: !nextUserMediation,
                })}
                onClick={this.handleGoNext}
              >
                <Icon svg="ico-next-w-group" />
              </button>
            </li>
          </ul>
        </div>
        {IS_DEV && (
          <div className="debug absolute left-0 ml2 p2">
            ({this.props.isLoadingBefore ? '?' : ' '}
            {this.props.previousLimit}){' '}
            {this.props.currentUserMediation &&
              this.props.currentUserMediation.index}{' '}
            ({this.props.nextLimit} {this.props.isLoadingAfter ? '?' : ' '}) /{' '}
            {this.props.userMediations && this.props.userMediations.length - 1}
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
      currentUserMediation: selectCurrentUserMediation(state),
      deprecatedUserMediations: state.data.deprecatedUserMediations,
      isFlipDisabled: selectIsFlipDisabled(state),
      isFlipped: state.verso.isFlipped,
      nextLimit: selectNextLimit(state),
      nextUserMediation: selectNextUserMediation(state),
      previousLimit: selectPreviousLimit(state),
      previousUserMediation: selectPreviousUserMediation(state),
      userMediations: state.data.userMediations,
      unFlippable: state.verso.unFlippable,
    }),
    { flip, unFlip }
  )
)(Deck)
