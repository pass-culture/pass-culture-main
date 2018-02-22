import React, { Component } from 'react'

import Loading from './Loading'

class LoadingCard extends Component {
  /*
  componentWillMount () {
    console.log('QDQSDQSDQ', this.props)
    this.props.searchNode && this.props.searchNode.focus()
  }
  */
  render () {
    return (
      <div className='card flex items-center justify-center'>
        <Loading />
      </div>
    )
  }
}

export default LoadingCard
