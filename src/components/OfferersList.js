import React from 'react'
import { connect } from 'react-redux'
import { AutoSizer, List } from 'react-virtualized'

import OffererItem from './OffererItem'
import selectOfferersRows from '../selectors/offerersRows'

const OfferersList = ({ offerersRows }) => {
  return (
    <div className="offerers-list">
        <AutoSizer>
        {
          ({width, height}) => offerersRows && offerersRows.length && <List
            height={height}
            rowCount={offerersRows.length}
            rowHeight={220}
            rowRenderer={({ index, key, style }) =>
              <div className="columns"
                key={key}
                style={style}
              >
                {
                  offerersRows[index].map((offerer, index) =>
                    <div className="column" key={index}>
                      <OffererItem {...offerer} />
                    </div>
                  )
                }
              </div>
            }
            width={width}
           />
         }
         </AutoSizer>
    </div>
  )
}

export default connect(
  () => (state, ownProps) =>
    ({ offerersRows: selectOfferersRows(state, ownProps) })
)(OfferersList)
