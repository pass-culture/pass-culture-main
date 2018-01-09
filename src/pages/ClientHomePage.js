import React, { Component } from 'react'
import { connect } from 'react-redux'

import SearchBar from '../components/SearchBar'
import { requestData } from '../reducers/request'

class ClientHomePage extends Component {
  componentWillMount () {
    this.props.requestData('GET', 'offers');
  }
  render () {
    const { offers } = this.props
    return (
        <main className='page flex'>
            <SearchBar />
        </main>
    )
  }
}

export default connect(({ request: { offers } }) => ({ offers }),
                        { requestData })(ClientHomePage)
