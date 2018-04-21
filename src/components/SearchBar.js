import React, { Component } from 'react'
import { connect } from 'react-redux'

import { requestData } from '../reducers/data'

class SearchBar extends Component {
  onChange = event => {
    const search = event.target.value
    this.props.requestData('GET', `offers?search=${search}`)
  }
  render() {
    return <input type="" className="search-bar" onChange={this.onChange} />
  }
}

export default connect(null, { requestData })(SearchBar)
