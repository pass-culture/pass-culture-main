import React, { Component } from 'react'
import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import PropTypes from 'prop-types'
import OfferTile from './OfferTile/OfferTile'
import Offers from '../domain/ValueObjects/Offers'

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
    const atLeastOneHit = hits.length > 0

    return atLeastOneHit ?
      <div className="module-wrapper">
        <h1>
          {display.title}
        </h1>
        <ul className={display.layout}>
          {hits.map(hit => (
            <OfferTile
              hit={hit}
              key={hit.offer.id}
            />)
          )}
        </ul>
      </div>
      : <div />
  }
}

Module.propTypes = {
  module: PropTypes.instanceOf(Offers).isRequired
}

export default Module
