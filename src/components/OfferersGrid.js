import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import OffererButton from './OffererButton'
import withLogin from '../hocs/withLogin'

const OfferersGrid = ({ offerers }) => {
  return (
    <div className='flex flex-wrap items-center justify-center p2'>
      {
        offerers && offerers.map((offerer, index) => (
          <OffererButton key={index} {...offerer} />
        ))
      }
    </div>
  )
}

export default compose(
  withLogin,
  connect(
    state => ({ offerers: state.user && state.user.userOfferers })
  )
)(OfferersGrid)
