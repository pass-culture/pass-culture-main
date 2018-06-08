import React, { Component } from 'react'
import { connect } from 'react-redux'
import { AutoSizer, List } from 'react-virtualized'

import OffererItem from './OffererItem'
import { requestData } from '../reducers/data'
import selectOfferers from '../selectors/offerers'

class OfferersList extends Component {

  componentDidMount () {
    this.handleRequestData ()
  }
  componentDidUpdate(prevProps) {
    if (prevProps.user !== this.props.user) {
      this.handleRequestData ()
    }
  }

  handleRequestData = () => {
    if (this.props.user) {
      this.props.requestData('GET', 'offerers')
    }
  }

  render () {
    const {
      offerers
    } = this.props

    return (
      <div className="offerers-list section">
        {offerers.map(o => <OffererItem offerer={o} />)}
      </div>
    )

    // TODO: decide if we keep the autosizer
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
                  <OffererItem offerer={offerers[index]} />
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
}

export default connect(
  state => ({
    offerers: selectOfferers(state) || [],
    user: state.user
  }),
  { requestData }
)(OfferersList)
