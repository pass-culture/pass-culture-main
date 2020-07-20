import PropTypes from 'prop-types'
import React, { Component } from 'react'
import SwipeableViews from 'react-swipeable-views'

import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { parseAlgoliaParameters } from '../domain/parseAlgoliaParameters'
import Offers from '../domain/ValueObjects/Offers'
import OfferTile from './OfferTile/OfferTile'

class Module extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hits: [],
      isSwitching: false,
    }
    this.swipeRatio = 0.2
  }

  componentDidMount() {
    const {
      module: { algolia },
    } = this.props
    const parsedParameters = parseAlgoliaParameters(algolia)

    fetchAlgolia(parsedParameters).then(data => {
      const { hits } = data
      this.setState({
        hits: hits,
      })
    })
  }

  onSwitching = () => this.setState({ isSwitching: true })

  onTransitionEnd = () => this.setState({ isSwitching: false })

  render() {
    const {
      historyPush,
      module: { display },
      row,
    } = this.props
    const { hits, isSwitching } = this.state
    const atLeastOneHit = hits.length > 0

    return (
      atLeastOneHit && (
        <div className="module-wrapper">
          <h1>
            {display.title}
          </h1>
          <ul>
            <SwipeableViews
              className={display.layout}
              disableLazyLoading
              enableMouseEvents
              hysteresis={this.swipeRatio}
              onSwitching={this.onSwitching}
              onTransitionEnd={this.onTransitionEnd}
              slideClassName="module-slides"
            >
              {hits.map(hit => (
                <OfferTile
                  historyPush={historyPush}
                  hit={hit}
                  isSwitching={isSwitching}
                  key={`${row}${hit.offer.id}`}
                />
              ))}
            </SwipeableViews>
          </ul>
        </div>
      )
    )
  }
}

Module.propTypes = {
  historyPush: PropTypes.func.isRequired,
  module: PropTypes.instanceOf(Offers).isRequired,
  row: PropTypes.number.isRequired,
}

export default Module
