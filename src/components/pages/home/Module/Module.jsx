import PropTypes from 'prop-types'
import React, { Component } from 'react'
import SwipeableViews from 'react-swipeable-views'

import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { parseAlgoliaParameters } from '../domain/parseAlgoliaParameters'
import Offers from '../domain/ValueObjects/Offers'
import OfferTile from './OfferTile/OfferTile'
import Icon from '../../../layout/Icon/Icon'

class Module extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hits: [],
      isSwitching: false
    }
    this.swipeRatio = 0.2
  }

  componentDidMount() {
    const {
      module: { algolia }
    } = this.props
    const parsedParameters = parseAlgoliaParameters(algolia)

    fetchAlgolia(parsedParameters).then(data => {
      const { hits } = data
      this.setState({
        hits: hits
      })
    })
  }

  onSwitching = () => this.setState({ isSwitching: true })

  onTransitionEnd = () => this.setState({ isSwitching: false })

  render() {
    const {
      historyPush,
      module: { cover, display },
      row
    } = this.props
    const { hits, isSwitching } = this.state
    const atLeastOneHit = hits.length > 0
    const tiles = cover ? [cover, ...hits] : [...hits]

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
              {tiles.map(tile => {
                if (!tile.offer) {
                  return (
                    <li
                      className="offer-cover-wrapper"
                      key={`${row}-offer-cover`}
                    >
                      <div className="ofw-image-wrapper">
                        <img
                          alt=""
                          className="ofw-image"
                          src={tile}
                        />
                        <div className="ofw-swipe-icon-wrapper">
                          <Icon
                            className="ofw-swipe-icon"
                            svg="ico-swipe-tile"
                          />
                        </div>
                      </div>
                    </li>
                  )
                } else {
                  return (
                    <OfferTile
                      historyPush={historyPush}
                      hit={tile}
                      isSwitching={isSwitching}
                      key={`${row}${tile.offer.id}`}
                    />
                  )
                }
              })}
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
  row: PropTypes.number.isRequired
}

export default Module
