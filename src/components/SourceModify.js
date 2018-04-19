import React from 'react'
import { connect } from 'react-redux'

import List from '../components/List'
import ProviderForm from '../components/ProviderForm'
import ProviderItem from '../components/ProviderItem'
import { NEW } from '../utils/config'

const SourceModify = ({ offererId, providers }) => {
  return (
    <div>
      <List className='mb1'
        ContentComponent={ProviderItem}
        elements={providers}
        extra={{ offererId }}
        FormComponent={ProviderForm}
        getBody={form => Object.assign({ offererId }, form.providersById[NEW])}
        getIsDisabled={form =>
          !form ||
          !form.providersById ||
          !form.providersById[NEW] ||
          (
            !form.providersById[NEW].groupSize ||
            !form.providersById[NEW].value
          )
        }
        getOptimistState={(state, action) => {
          /*
          let optimistProviders = [action.config.body]
          if (providers) {
            optimistProviders = optimistProviders.concat(providers)
          }
          return {
            providers: optimistProviders
          }
          */
        }}
        getSuccessState={(state, action) => {
          /*
          const offerIds = state.offers.map(({ id }) => id)
          const offerIndex = offerIds.indexOf(id)
          const nextOffers = [...state.offers]
          nextOffers[offerIndex] = Object.assign({}, nextOffers[offerIndex], {
            providers: [action.data].concat(nextOffers[offerIndex].providers)
          })
          // on success we need to make this buffer
          // null again in order to catch the new refreshed ownProps.providers
          return { offers: nextOffers, providers: null }
          */
        }}
        isWrap
        path='providers'
        title='providers' />
    </div>
  )
}

export default connect(
  state => ({ offererId: state.data.offerers && state.data.offerers[0] &&
    state.data.offerers[0].id })
)(SourceModify)
