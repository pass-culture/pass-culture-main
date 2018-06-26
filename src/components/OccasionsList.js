import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { compose } from 'redux'

import OccasionItem from './OccasionItem'
import createSearchSelector from '../selectors/createSearch'
import createOccasionsSelector from '../selectors/createOccasions'

const OccasionsList = ({ occasions }) => {
  if (!occasions) return null;
  return (
    <ul className='occasions-list pc-list'>
      {
        occasions.map(o =>
          <OccasionItem key={o.id} occasion={o} />)
      }
    </ul>
  )
}

const searchSelector = createSearchSelector()
const occasionsSelector = createOccasionsSelector()

export default compose(
  withRouter,
  connect(
    (state, ownProps) => {
      const { offererId, venueId } = searchSelector(state, ownProps.location.search)
      return {
        occasions: occasionsSelector(state, offererId, venueId)
      }
    }
  )
)(OccasionsList)
