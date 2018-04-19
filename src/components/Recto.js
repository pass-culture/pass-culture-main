import classnames from 'classnames'
import React, { Component } from 'react'
import { connect } from 'react-redux'

import { getOffer } from '../selectors/offer'
import { getMediation } from '../selectors/mediation'
import selectOffer from '../selectors/offer'
import { getSource } from '../selectors/source'
import { getThumbUrl } from '../selectors/thumbUrl'
import selectUserMediation from '../selectors/userMediation'
import { IS_DEV } from '../utils/config'


class Recto extends Component {
  constructor () {
    super()
    this.state = {
      id: null,
      mediation: null,
      offer: null,
      thumbUrl: null
    }
  }

  static getDerivedStateFromProps (nextProps, prevState) {
    const {
      currentOffer,
      currentUserMediation,
      id,
      userMediations
    } = nextProps
    // UPDATE WHEN ID CHANGES
    if (!id
      || !userMediations
      || id === prevState.id
      || !currentUserMediation) {
      return {}
    }
    // NO NEED TO FIND AGAIN IF WE ARE THE CURRENT USER MEDIATION
    let userMediation
    if (currentUserMediation.id === id) {
      userMediation = currentUserMediation
    } else {
      userMediation = userMediations.find(um => um.id === id)
    }
    // FIND THE ASSOCIATED OFFER
    let offer
    if (currentUserMediation.id === userMediation.id) {
      offer = currentOffer
    } else {
      const userMediationOffers = userMediation.userMediationOffers
      if (userMediation.userMediationOffers && userMediation.userMediationOffers.length) {
        const offerId = userMediationOffers[
          Math.floor(Math.random() * userMediationOffers.length)].id
        offer = getOffer(userMediation, offerId)
      }
    }
    // GET OTHER PROPERTIES
    const mediation = getMediation(userMediation)
    const source = getSource(mediation, offer)
    const thumbUrl = getThumbUrl(mediation, source, offer)
    return {
      id,
      mediation,
      offer,
      thumbUrl
    }
  }

  render () {
    const {
      dateRead,
      id,
      index,
      isFlipped
    } = this.props
    const {
      mediation,
      offer,
      thumbUrl,
    } = this.state
    const backgroundStyle = { backgroundImage: `url('${thumbUrl}')` };
    const thumbStyle = Object.assign({}, backgroundStyle);
    if (mediation) {
      thumbStyle.backgroundSize='cover';
    }
    return (
      <div className='recto'>
        <div className='background' style={backgroundStyle} />
        {
          thumbUrl && (
            <div style={thumbStyle} className={classnames('thumb', {
              translated: isFlipped
            })} />
          )
        }
        {
          IS_DEV && (
            <div className='debug absolute left-0 ml2 p2'>
              <span>
                {id} {offer && offer.id} {index}
              </span>
              {
                dateRead && [
                  <span key={0}>
                    &middot;
                  </span>,
                  <span key={1}>
                    {dateRead}
                  </span>
                ]
              }
            </div>
          )
        }
     </div>
    )
  }
}

export default connect(
  (state, ownProps) => ({
    currentOffer: selectOffer(state),
    currentUserMediation: selectUserMediation(state),
    isFlipped: state.verso.isFlipped,
    userMediations: state.data.userMediations
  })
)(Recto)
