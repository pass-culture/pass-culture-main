import React from 'react'
import { connect } from 'react-redux'
import { compose } from 'redux'

import OffererItem from './OffererItem'

const OfferersGrid = ({ offerers }) => {
  return (
    <div className="flex flex-wrap items-center justify-center p2">
      {offerers &&
        offerers.map((offerer, index) => (
          <OffererItem key={index} {...offerer} />
        ))}
    </div>
  )
}

export default compose(
  connect(state => ({ offerers: state.user && state.user.userOfferers }))
)(OfferersGrid)
