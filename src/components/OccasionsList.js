import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import OccasionItem from './OccasionItem'
import selectOccasions from '../selectors/occasions'

const OccasionsList = ({ occasions }) => {
  if (!occasions) return null;
  return (
    <ul className='occasions-list pc-list'>
      {occasions.map(o => <OccasionItem key={o.id} occasion={o} />)}
    </ul>
  )
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({
      occasions: selectOccasions(state, ownProps)
    })
  )
)(OccasionsList)
