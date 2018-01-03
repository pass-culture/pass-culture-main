import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestGetProducts } from '../reducers/request'

class ActivitiesPage extends Component {
  componentWillMount() {
    this.props.requestGetProducts()
  }
  render () {
    const { products } = this.props
    return (
      <main>
        {
          products && products.map(({ type }, index) => (
            <div key={index}>
              {type}
            </div>
          ))
        }
      </main>
    )
  }
}

export default connect(({ request: { products } }) => ({ products }),
  { requestGetProducts }
)(ActivitiesPage)
