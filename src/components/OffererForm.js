import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import ProviderItem from './ProviderItem'
import withSelectors from '../hocs/withSelectors'

const OffererForm = ({ providers }) => {
  return (
    <div className='offer-setting'>
      <div className='h2 mb1'>
        Mes sources
      </div>
      <div className='p3' >
      {
        providers && providers.map((provider, index) =>
          <ProviderItem key={index} {...provider} />)
      }
      </div>
    </div>
  )
}

export default compose(
  connect(
    state => Object.assign({
      offerProviders: state.data.offerers && state.data.offerers[0] &&
        state.data.offerers[0].offerProviders,
      providers: state.data.providers
    }, state.user && state.user.offerer)
  ),
  withSelectors({
    providers: [
      ownProps => ownProps.providers,
      ownProps => ownProps.offerProviders,
      (providers, offerProviders) => {
        const offerProviderPairs = offerProviders && offerProviders
          .map(offerProvider => offerProvider.split(':'))
        return providers.map(({ id, name }) => {
          return {
            ids: offerProviderPairs && offerProviderPairs
              .filter(offerProviderPair => offerProviderPair[0] === id)
              .map(offerProviderPair => offerProviderPair[1]),
            name
          }
        })
      }
    ]
  })
)(OffererForm)
