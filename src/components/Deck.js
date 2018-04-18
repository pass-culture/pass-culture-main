import classnames from 'classnames'
import get from 'lodash.get'
import Draggable from 'react-draggable'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'
import withSizes from 'react-sizes'
import { withRouter } from 'react-router-dom'

import Card from './Card'
import Clue from './Clue'
import Icon from './Icon'
import { flip, unFlip } from '../reducers/verso'
import selectIsFlipDisabled from '../selectors/isFlipDisabled'
import selectHeaderColor from '../selectors/headerColor'
import { getMediation } from '../selectors/mediation'
import selectNextLimit from '../selectors/nextLimit'
import selectNextUserMediation from '../selectors/nextUserMediation'
import selectPreviousLimit from '../selectors/previousLimit'
import selectPreviousUserMediation from '../selectors/previousUserMediation'
import { getOffer } from '../selectors/offer'
import selectUserMediation from '../selectors/userMediation'
import { IS_DEV, MOBILE_OS, ROOT_PATH } from '../utils/config';
import { getDiscoveryPath } from '../utils/routes'
import { worker } from '../workers/dexie/register'

class Deck extends Component {
  constructor () {
    super()
    this.state = {
      bgStyle: null,
      previousBgStyle: null,
      position: null,
      refreshKey: 0
    }
  }

  handleDeprecatedData = nextProps => {
    // DEPRECATION HANDLING
    // IF THE RECO ARE DEPRECATED, WE GO TO DECOUVERTE
    const { deprecatedUserMediations } = nextProps
    if (deprecatedUserMediations
      && deprecatedUserMediations !== this.props.deprecatedUserMediations) {
      nextProps.history.push('/decouverte')
    }
  }

  handleGoNext = () => {
    const { history,
      isFlipped,
      nextUserMediation
    } = this.props
    if (!nextUserMediation || isFlipped) return;
    const offer = getOffer(nextUserMediation)
    history.push(getDiscoveryPath(offer, getMediation(nextUserMediation)));
    this.handleRefreshNext()
  }

  handleGoPrevious = () => {
    const { history,
      isFlipped,
      previousUserMediation
    } = this.props
    if (!previousUserMediation || isFlipped) return;
    const offer = getOffer(previousUserMediation)
    history.push(getDiscoveryPath(offer, getMediation(previousUserMediation)));
    this.handleRefreshPrevious()
  }

  handleRefreshPrevious = () => {
    const { currentUserMediation, previousLimit } = this.props
    if (currentUserMediation.index <= previousLimit) {
      worker.postMessage({ key: 'dexie-push-pull',
        state: { around: currentUserMediation.id }})
    }
  }

  handleRefreshNext = () => {
    const { currentUserMediation, nextLimit } = this.props
    if (currentUserMediation.index >= nextLimit) {
      worker.postMessage({ key: 'dexie-push-pull',
        state: { around: currentUserMediation.id }})
    }
  }

  handleRefreshedData = nextProps => {
    // REFRESH HANDLING
    // (ie kill the transition the short time we change the blob)
    // WE CHANGE THE KEY OF THE DRAGGABLE
    // TO FORCE IT TO REMOUNT AGAIN
    if (nextProps && (
         (!nextProps.userMediations || !this.props.userMediations)
         || (nextProps.userMediations === this.props.userMediations)
         || (!nextProps.currentUserMediation || !this.props.currentUserMediation)
         || (nextProps.currentUserMediation.index === this.props.currentUserMediation.index)
       )
    ) {
      return
    }
    this.setState({ refreshKey: this.state.refreshKey + 1 })
  }

  handleSetDragPosition = nextProps => {
    const props = nextProps || this.props
    if (nextProps
      && nextProps.currentUserMediation === this.props.currentUserMediation
      && nextProps.width === this.props.width
    ) { return }
    const offsetWidth = get(this.$deck, 'offsetWidth')
    const index = get(props, 'currentUserMediation.index', 0)
    const x = -1 * offsetWidth * index
    const position = { x, y: 0 }
    this.setState({ position })
  }

  onStop = (e, data) => {
    const { flip,
      horizontalSlideRatio,
      verticalSlideRatio,
      unFlip
    } = this.props
    const deckWidth = this.$deck.offsetWidth;
    const deckHeight = this.$deck.offsetHeight;
    const index = get(this.props, 'currentUserMediation.index', 0)
    const offset = (data.x + deckWidth * index)/deckWidth
    if (offset > horizontalSlideRatio) {
      this.handleGoPrevious();
    } else if (-offset > horizontalSlideRatio) {
      this.handleGoNext();
    } else if (data.y > deckHeight * verticalSlideRatio) {
      unFlip();
    } else if (data.y < -deckHeight * verticalSlideRatio) {
      flip();
    }
  }

  componentDidMount () {
    this.handleRefreshedData()
    this.handleSetDragPosition()
  }

  componentWillReceiveProps (nextProps) {
    this.handleRefreshedData(nextProps)
    this.handleDeprecatedData(nextProps)
    this.handleSetDragPosition(nextProps)
  }

  render () {
    const {
      currentUserMediation,
      flip,
      isFlipDisabled,
      isFlipped,
      nextUserMediation,
      previousUserMediation,
      unFlip,
      unFlippable,
    } = this.props
    const {
      position,
      refreshKey
    } = this.state
    return (
      <div className='deck'
        id='deck'
        ref={$el => (this.$deck = $el)}>
        {!unFlippable && (
          <button className={classnames('button close', {
              hidden: !isFlipped,
            })}
            onClick={unFlip} >
            <Icon svg='ico-close' />
          </button>
        )}
        <div className={classnames('loading flex items-center justify-center', {
          'shown': !currentUserMediation
        })}>
          <div>
            <Icon draggable={false} svg='ico-loading-card' />
            <div className='h2'>
              chargement des offres
            </div>
          </div>
        </div>
        <Draggable
          axis={isFlipped ? 'none' : 'exclude'}
          key={refreshKey}
          position={position}
          onStop={this.onStop}
          bounds={isFlipped ? {} : {bottom: 0}}
          >
          <div>
            {
              previousUserMediation && <Card position='previous'
                userMediation={previousUserMediation} />
            }
            <Card ref={$el => this.$current = $el}
              position='current'
              userMediation={currentUserMediation} />
            {
              nextUserMediation && <Card position='next'
                userMediation={nextUserMediation} />
            }
          </div>
        </Draggable>
        <div className={classnames('board-wrapper', { hidden: isFlipped })}>
          <div className='board-bg'
            style={{ background: `linear-gradient(to bottom, rgba(0,0,0,0) 0%,${this.props.headerColor} 25%,${this.props.headerColor} 100%)` }} />
          <ul className={classnames('controls', {
            hidden: isFlipped,
          })} style={{backgroundImage: `url('${ROOT_PATH}/mosaic-w@2x.png')`,}} >
            <li>
              <button className={classnames('button before', {
                  hidden: !previousUserMediation,
                })}
                onClick={this.handleGoPrevious} >
                  <Icon svg='ico-prev-w-group' />
              </button>
            </li>
            <li>
              <button className={classnames('button to-recto', {
                  hidden: isFlipDisabled,
                })}
                disabled={isFlipDisabled}
                onClick={flip} >
                <Icon svg='ico-slideup-w' />
              </button>
              <Clue />
            </li>
            <li>
              <button className={classnames('after button', {
                  hidden: !nextUserMediation,
                })}
                onClick={this.handleGoNext} >
                <Icon svg='ico-next-w-group' />
              </button>
            </li>
          </ul>
        </div>
        {
          IS_DEV && (
            <div className='debug absolute left-0 ml2 p2'>
              ({this.props.isLoadingBefore ? '?' : ' '}{this.props.previousLimit}) {this.props.currentUserMediation && this.props.currentUserMediation.index}{' '}
              ({this.props.nextLimit} {this.props.isLoadingAfter ? '?' : ' '}) / {this.props.userMediations && this.props.userMediations.length - 1}
            </div>
          )
        }
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
  transitionTimeout: 500
}


export default compose(
  withRouter,
  connect(
    state => ({
      currentUserMediation: selectUserMediation(state),
      deprecatedUserMediations: state.data.deprecatedUserMediations,
      headerColor: selectHeaderColor(state),
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
  ),
  ...MOBILE_OS === 'unknown' && [withSizes(({ width }) => ({ width }))]
)(Deck)
