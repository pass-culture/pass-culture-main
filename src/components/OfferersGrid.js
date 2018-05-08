import React from 'react'
import { connect } from 'react-redux'
import { AutoSizer, List } from 'react-virtualized'

import OffererItem from './OffererItem'
import selectOfferersRows from '../selectors/offerersRows'

const OfferersGrid = ({ offerersRows }) => {
  return (
    <div className="offerers-grid">
        <AutoSizer>
        {
          ({width, height}) => offerersRows && offerersRows.length && <List
            height={height}
            rowCount={offerersRows.length}
            rowHeight={220}
            rowRenderer={({ index, key, style }) =>
              <div key={key}
              style={style}>
                <div className="columns">
                  {
                    offerersRows[index].map((offerer, index) =>
                      <div className="column" key={index}>
                        <OffererItem {...offerer} />
                      </div>
                    )
                  }
                </div>
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
)(OfferersGrid)
