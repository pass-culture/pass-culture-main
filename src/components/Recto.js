import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import RectoDebug from './RectoDebug'
import Loading from './Loading'
import withSelectors from '../hocs/withSelectors'
import { getOffer } from '../selectors/offer'
import { getMediation } from '../selectors/mediation'
import selectOffer from '../selectors/offer'
import { getSource } from '../selectors/source'
import { getThumbUrl } from '../selectors/thumbUrl'
import selectUserMediation from '../selectors/userMediation'
import { IS_DEV } from '../utils/config'

const Recto = props => {
  const { offer,
    isLoading,
    thumbUrl
  } = props
  const style = isLoading
    ? { backgroundColor: 'black' }
    : { backgroundImage: `url('${thumbUrl}')` }
  return (
    <div className='recto'>
       <div className={classnames('card-background', {
           'card-background--loading flex items-center justify-center': isLoading
         })} style={style}>
        {isLoading && <Loading isForceActive />}
      </div>
      { offer && (
        <div>
          <img alt='thumb'
            draggable={false}
            src={thumbUrl}
          />
          {IS_DEV && <RectoDebug {...props} />}
        </div>
      )}
     </div>
  )
}

export default compose(
  connect(
    (state, ownProps) => ({
      currentOffer: selectOffer(state),
      currentUserMediation: selectUserMediation(state),
      isFlipped: state.navigation.isFlipped,
      userMediations: state.data.userMediations
    })),
  withSelectors({
    userMediation: [
      ownProps => ownProps.id,
      ownProps => ownProps.userMediations,
      (id, userMediations) => id && userMediations &&
        userMediations.find(um => um.id === id)
    ],
    offer: [
      ownProps => ownProps.currentUserMediation,
      ownProps => ownProps.currentOffer,
      (ownProps, nextState) => nextState.userMediation,
      (currentUserMediation, currentOffer, userMediation) => {
        if (!currentUserMediation || !userMediation) {
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
      (ownProps, nextState) => nextState.userMediation,
      (ownProps, nextState) => nextState.offer,
      (userMediation, offer) => {
        if (!userMediation) {
          return
        }
        const mediation = getMediation(userMediation)
        const source = getSource(mediation, offer)
        return getThumbUrl(mediation, source, offer)
      }
    ]
  })
)(Recto)
