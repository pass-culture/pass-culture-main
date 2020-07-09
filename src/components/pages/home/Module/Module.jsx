import React, { Component } from 'react'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import PropTypes from 'prop-types'
import OfferTile from './OfferTile/OfferTile'

class Module extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hits: []
    }
  }

  componentDidMount() {
    fetchAlgolia().then(data => {
      const { hits } = data
      this.setState({
        hits: hits
      })
    })
  }

  render() {
    const { module: { display } } = this.props
    const { hits } = this.state

    return (
      <div>
        <ul className={display.layout}>
          {hits.length > 0 && hits.map(hit => (
            <OfferTile
              hit={hit}
              key={hit.offer.id}
            />)
          )}
        </ul>
      </div>
    )
  }
}

Module.propTypes = {
  module: PropTypes.shape({
    algolia: PropTypes.shape(),
    display: PropTypes.shape()
  }).isRequired
}

export default Module
