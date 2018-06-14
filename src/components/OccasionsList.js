import React from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { AutoSizer, List } from 'react-virtualized'
import { compose } from 'redux'

import OccasionItem from './OccasionItem'
import selectOccasions from '../selectors/occasions'

const OccasionsList = ({ occasions }) => {
  if (!occasions) return null;
  return (
    <ul className='occasions-list pc-list'>
      {occasions.map(o => <OccasionItem key={o.id} {...o} />)}
    </ul>
  )

  return (
    <div className="occasions-list">
      <AutoSizer>
      {
        ({width, height}) => <List
            height={height}
            rowCount={occasions.length}
            rowHeight={190}
            rowRenderer={({ index, key, style }) => (
              <div key={index} style={style}>
                <OccasionItem {...occasions[index]} />
              </div>
            )}
            width={width}
          />
      }
      </AutoSizer>
    </div>
  )
}

export default compose(
  withRouter,
  connect(
    (state, ownProps) => ({
      occasions: selectOccasions(state, ownProps),
      user: state.user
    }),
    // { assignData, requestData }
  )
)(OccasionsList)
