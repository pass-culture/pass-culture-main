import React from 'react'
import { connect } from 'react-redux'
import { AutoSizer, List } from 'react-virtualized'

import OffererItem from './OffererItem'

const OfferersList = ({ offerers }) => {
  return (
    <div className="offerers-list is-6">
        <AutoSizer>
        {
          ({width, height}) => offerers && <List
            width={0.95 * width}
            height={height}
            rowCount={offerers.length}
            rowHeight={120}
            rowRenderer={({ index, key, style }) => (
              <OffererItem
                key={index}
                {...offerers[index]}
                style={style}
              />
            )}
           />
         }
         </AutoSizer>
    </div>
  )
}

export default connect(
  state => ({ offerers: state.user && state.user.offerers })
)(OfferersList)
