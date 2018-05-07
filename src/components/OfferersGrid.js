import React from 'react'
import { connect } from 'react-redux'
import withSizes from 'react-sizes'
import { List } from 'react-virtualized'
import { compose } from 'redux'

import OffererItem from './OffererItem'

const OfferersGrid = ({ height,
  offerers,
  width
}) => {
  return (
    <div className="columns">
      {
        offerers && <List
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
    </div>
  )
}

OfferersGrid.defaultProps = {
  height: 1500,
  width: 1500
}

export default compose(
  withSizes(({ width, height }) => ({
    width,
    height
  })),
  connect(state => ({ offerers: state.user && state.user.offerers }))
)(OfferersGrid)
