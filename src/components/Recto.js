import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import RectoDebug from './RectoDebug'
import withSelectors from '../hocs/withSelectors'
import { getOffer } from '../selectors/offer'
import { getMediation } from '../selectors/mediation'
import selectOffer from '../selectors/offer'
import { getSource } from '../selectors/source'
import { getThumbUrl } from '../selectors/thumbUrl'
import selectUserMediation from '../selectors/userMediation'
import { IS_DEV } from '../utils/config'

import Icon from './Icon'

class Recto extends Component {
  constructor () {
    super()
    this.state = { isRemoveLoading: false }
  }

  handleRemoveLoading = () => {
    this.removeLoadingTimeout = setTimeout(() =>
      this.setState({ isRemoveLoading: true }), 0)
  }

  componentDidMount () {
    if (this.props.isRebootLoading) {
      this.handleRemoveLoading()
    }
  }

  componentWillReceiveProps (nextProps) {
    if (!nextProps.isRebootLoading && nextProps.isFromLoading && !this.props.isFromLoading) {
      this.handleRemoveLoading()
    }
  }

  componentWillUnmount () {
    this.removeLoadingTimeout && clearTimeout(this.removeLoadingTimeout)
  }

  render () {
    const { isFromLoading,
      mediation,
      isLoading,
      thumbUrl,
      isFlipped,
    } = this.props
    const { isRemoveLoading } = this.state
    const backgroundStyle = { backgroundImage: `url('${thumbUrl}')` };
    const thumbStyle = Object.assign({}, backgroundStyle);
    if (mediation) {
      thumbStyle.backgroundSize='cover';
    }
    return (
      <div className='recto'>
        <div className='card-background' style={backgroundStyle} />
        {
          (isLoading || isFromLoading) && (
            <div className={classnames('loading flex items-center justify-center', {
              'loading--ended': isRemoveLoading
            })}>
              <div>
                <Icon svg='ico-loading-card' />
                <div className='h2'>
                  chargement des offres
                </div>
              </div>
           </div>
          )
        }
        { thumbUrl && (
          <div style={thumbStyle} className={classnames('thumb', {
            translated: isFlipped
          })} />
        )}
        {IS_DEV && <RectoDebug {...this.props} />}
     </div>
    )
  }
}

export default compose(
  connect(
    (state, ownProps) => ({
      currentOffer: selectOffer(state),
      currentUserMediation: selectUserMediation(state),
      isFlipped: state.verso.isFlipped,
      userMediations: state.data.userMediations
    })),
  withSelectors({
    userMediation: [
      ownProps => ownProps.id,
      ownProps => ownProps.userMediations,
      (id, userMediations) => id && userMediations &&
        userMediations.find(um => um.id === id)
    ],
    mediation: [
      (ownProps, nextState) => nextState.userMediation,
      userMediation => getMediation(userMediation)
    ],
    offer: [
      ownProps => ownProps.currentUserMediation,
      ownProps => ownProps.currentOffer,
      (ownProps, nextState) => nextState.userMediation,
      (currentUserMediation, currentOffer, userMediation) => {
        if (!currentUserMediation
            || !userMediation
            || !userMediation.userMediationOffers
            || userMediation.userMediationOffers.length === 0) {
          return
        }
        if (currentUserMediation.id === userMediation.id) {
          return currentOffer
        }
        const userMediationOffers = userMediation.userMediationOffers
        const offerId = userMediationOffers[
          Math.floor(Math.random() * userMediationOffers.length)].id
        return getOffer(offerId, userMediation)
      }
    ],
    thumbUrl: [
      (ownProps, nextState) => nextState.mediation,
      (ownProps, nextState) => nextState.offer,
      (mediation, offer) => {
        const source = getSource(mediation, offer)
        return getThumbUrl(mediation, source, offer)
      }
    ]
  })
)(Recto)
