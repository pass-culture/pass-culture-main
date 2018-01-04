import React, { Component } from 'react'
import { connect } from 'react-redux'

import SpreadsheetItem from '../components/SpreadsheetItem'
import { requestGetProducts } from '../reducers/request'

class SpreadsheetPage extends Component {
  componentWillMount() {
    this.props.requestGetProducts()
  }
  render () {
    const { products } = this.props
    return (
      <main>
        {
          products && products.map((product, index) => (
            <SpreadsheetItem key={index} {...product} />
          ))
        }
      </main>
    )
  }
}

export default connect(({ request: { products } }) => ({ products }),
  { requestGetProducts }
)(SpreadsheetPage)
