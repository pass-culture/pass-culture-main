import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import MediationCardBack from '../components/MediationCardBack'
import OfferInfo from '../components/OfferInfo'
import withLogin from '../hocs/withLogin'
import { requestData } from '../reducers/data'

class ClientOfferPage extends Component {
  componentWillMount = () => {
    const { requestData, offerId, mediationId } = this.props;
    requestData('GET', 'offers/' + offerId)
  }
  render = () => {
    const { offer, offerId, mediationId } = this.props
    var mediation
    if (mediationId) {
      for (var m of (offer.thing ? offer.thing.mediations : offer.event.mediations)) {
        if (m.id === mediationId) {
          mediation = m
          break
        }
      }
    }
    return (
      <main className='page client-offer-page flex flex-column'>
        { mediation && <MediationCardBack {...mediation} /> }
        { offer && offerId !== '0' && <OfferInfo {...offer} /> }
      </main>
    )
  }
}

export default compose(
  withLogin(),
  connect(
    (state, ownProps) => ({
      offer: state.data['offers/'+ownProps.offerId] &&
        state.data['offers/'+ownProps.offerId][0]
    }),
    { requestData }
  )
)(ClientOfferPage)
