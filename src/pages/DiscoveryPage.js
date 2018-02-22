import React, { Component } from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import Explorer from '../components/Explorer'
import withLogin from '../hocs/withLogin'
import { assignData } from '../reducers/data'
import { requestUserMediationsData } from '../utils/sync'

class DiscoveryPage extends Component {
  handleSearchHook = (method, path, result, config) => {
     const { assignData, requestUserMediationsData } = this.props
     if (!result.data) {
       return
     }
     if (config.value &&  config.value.length > 0) {
       const userMediations = result.data.map(offer => ({
         isClicked: false,
         isFavorite: false,
         offer
       }))
       assignData({ userMediations })
     } else {
       requestUserMediationsData()
     }
  }
  render () {
    return (
      <main className='page discovery-page center'>
        <Explorer collectionName='userMediations'
          searchCollectionName='offers'
          searchHook={this.handleSearchHook} />
      </main>
    )
  }
}

export default compose(
  withLogin,
  connect(
    null,
    { assignData, requestUserMediationsData }
  )
)(DiscoveryPage)
