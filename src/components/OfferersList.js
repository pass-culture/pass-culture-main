import React from 'react'
import { connect } from 'react-redux'
import { AutoSizer, List } from 'react-virtualized'

import OffererItem from './OffererItem'

const OfferersList = ({ offerers }) => {
  return (
    <div className="offerers-list">
      <AutoSizer>
      {
        ({width, height}) => offerers && offerers.length
          ? <List
            height={height}
            rowCount={offerers.length}
            rowHeight={190}
            rowRenderer={({ index, key, style }) => (
              <div key={index} style={style}>
                <OffererItem {...offerers[index]} />
              </div>
            )}
            width={width}
          />
          : ''
      }
      </AutoSizer>
    </div>
  )
}

export default connect(
  (state, ownProps) => ({
    offerers: state.user && state.user.offerers
  })
)(OfferersList)
