import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/request'

class SearchBar extends Component {
  onChange = (event) => {
    this.props.requestData('GET', 'offers')
  }
  render () {
    return (
      <input type='' className='search-bar' onChange={this.onChange} />
    )
  }
}

export default connect(null, { requestData })(SearchBar)
