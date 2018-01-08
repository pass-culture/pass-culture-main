import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/request'

class ActivitiesPage extends Component {
  componentWillMount() {
    this.props.requestData('GET', 'pro/offers')
  }
  render () {
    const { offers } = this.props
    return (
      <main>
        {
          offers && offers.map(({ type }, index) => (
            <div key={index}>
              {type}
            </div>
          ))
        }
      </main>
    )
  }
}

export default connect(({ request: { offers } }) => ({ offers }),
  { requestData }
)(ActivitiesPage)
