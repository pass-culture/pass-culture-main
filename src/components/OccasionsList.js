import React, { Component } from 'react'
import { connect } from 'react-redux'
import { withRouter } from 'react-router'
import { AutoSizer, List } from 'react-virtualized'
import { compose } from 'redux'

import OccasionItem from './OccasionItem'
import selectOccasions from '../selectors/occasions'

class OccasionsList extends Component {
  // handleRequestData = () => {
  //   this.props.requestData('GET', `occasions`)
  // }

  // componentWillMount() {
  //   this.props.user && this.handleRequestData()
  // }

  // componentDidUpdate(prevProps) {
  //   const { user } = this.props
  //   if (user && user !== prevProps.user) {
  //     this.handleRequestData()
  //   }
  // }

  // componentWillUnmount () {
  //   this.props.assignData({ occasions: null })
  // }

  render() {
    const { occasions } = this.props
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
}

export default compose(
  withRouter,
  connect(
    state => ({
      occasions: selectOccasions(state),
      user: state.user
    }),
    // { assignData, requestData }
  )
)(OccasionsList)
