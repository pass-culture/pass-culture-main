import classnames from 'classnames'
import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import RectoDebug from './RectoDebug'
import Loading from './Loading'
import withSelectors from '../hocs/withSelectors'
import { getOffer } from '../selectors/offer'
import { getMediation } from '../selectors/mediation'
import { getSource } from '../selectors/source'
import { getThumbUrl } from '../selectors/thumbUrl'
import { IS_DEV } from '../utils/config'

const Recto = props => {
  const {
    id,
    isLoading,
    item,
    thumbUrl
  } = props
  const style = isLoading
    ? { backgroundColor: 'black' }
    : { backgroundImage: `url('${thumbUrl}')`}
  return (
    <div className='recto'>
       <div className={classnames('card-background', {
           'card-background--loading flex items-center justify-center': isLoading
         })} style={style}>
        {isLoading && <Loading isForceActive />}
      </div>
      { id && (
        <div>
          <img alt='thumb'
            src={thumbUrl} />
          {IS_DEV && <RectoDebug {...props} />}
        </div>
      )}
     </div>
  )
}

export default compose(
  connect(
    (state, ownProps) => ({
      isFlipped: state.navigation.isFlipped,
      userMediations: state.data.userMediations
    })),
  withSelectors({
    userMediation: [
      ownProps => ownProps.id,
      ownProps => ownProps.userMediations,
      (id, userMediations) => id && userMediations.find(um => um.id === id)
    ],
    thumbUrl: [
      (ownProps, nextState) => nextState.userMediation,
      userMediation => {
        if (!userMediation) {
          return
        }
        const mediation = getMediation(userMediation)
        const userMediationOffers = userMediation.userMediationOffers
        const offerId = userMediationOffers[
          Math.floor(Math.random() * userMediationOffers.length)].id
        const offer = getOffer(offerId, userMediation)
        const source = getSource(mediation, offer)
        return getThumbUrl(mediation, source, offer)
      }
    ]
  })
)(Recto)
