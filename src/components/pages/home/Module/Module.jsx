import PropTypes from 'prop-types'
import React, { Component } from 'react'
import SwipeableViews from 'react-swipeable-views'

import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { PANE_LAYOUT } from '../domain/layout'
import { parseAlgoliaParameters } from '../domain/parseAlgoliaParameters'
import Offers from '../domain/ValueObjects/Offers'
import OffersWithCover from '../domain/ValueObjects/OffersWithCover'
import { buildPairedTiles, buildTiles } from './domain/buildTiles'
import OneItem from './OneItem/OneItem'
import TwoItems from './TwoItems/TwoItems'

class Module extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hits: [],
      isSwitching: false,
      nbHits: 0,
      parsedParameters: null,
      tilesTracking: {
        haveSeenAllTiles: false,
        numberOfTiles: 0,
      },
    }
    this.swipeRatio = 0.2
  }

  componentDidMount() {
    const {
      geolocation,
      module: { algolia },
    } = this.props
    const parsedParameters = parseAlgoliaParameters({ geolocation, parameters: algolia })

    if (parsedParameters) {
      fetchAlgolia(parsedParameters).then(data => {
        const { hits, nbHits } = data
        this.setState({
          hits: hits,
          nbHits: nbHits,
          parsedParameters: parsedParameters,
        })
      })
    }
  }

  componentDidUpdate(prevProps, prevState) {
    const {
      tilesTracking: { haveSeenAllTiles, numberOfTiles },
    } = this.state
    const {
      trackAllTilesSeen,
      module: { display: { title = 'Missing title' } = {} },
    } = this.props
    if (prevState.tilesTracking.haveSeenAllTiles !== haveSeenAllTiles) {
      trackAllTilesSeen(title, numberOfTiles)
    }
  }

  onChangeIndex = numberOfTiles => index => {
    if (index + 1 === numberOfTiles) {
      this.setState({ tilesTracking: { haveSeenAllTiles: true, numberOfTiles } })
    }
  }

  onSwitching = () => {
    this.setState({ isSwitching: true })
  }

  onTransitionEnd = () => {
    this.setState({ isSwitching: false })
  }

  render() {
    const {
      historyPush,
      module: {
        algolia,
        cover,
        display: { layout = PANE_LAYOUT['ONE-ITEM-MEDIUM'], minOffers = 0, title } = {},
      },
      row,
    } = this.props
    const { hits, isSwitching, nbHits, parsedParameters } = this.state
    const atLeastOneHit = hits.length > 0
    const minOffersHasBeenReached = nbHits >= minOffers
    const shouldModuleBeDisplayed = atLeastOneHit && minOffersHasBeenReached
    const isOneItemLayout = layout === PANE_LAYOUT['ONE-ITEM-MEDIUM']
    const tiles = isOneItemLayout
      ? buildTiles({ algolia, cover, hits, nbHits })
      : buildPairedTiles({ algolia, cover, hits, nbHits })

    return (
      shouldModuleBeDisplayed && (
        <section className="module-wrapper">
          <h1>
            {title}
          </h1>
          <ul>
            <SwipeableViews
              className={layout || PANE_LAYOUT['ONE-ITEM-MEDIUM']}
              disableLazyLoading
              enableMouseEvents
              hysteresis={this.swipeRatio}
              onChangeIndex={this.onChangeIndex(tiles.length)}
              onSwitching={this.onSwitching}
              onTransitionEnd={this.onTransitionEnd}
              resistance
              slideClassName="module-slides"
            >
              {tiles.map((tile, index) => {
                return isOneItemLayout ? (
                  <OneItem
                    historyPush={historyPush}
                    isSwitching={isSwitching}
                    // eslint-disable-next-line react/no-array-index-key
                    key={`${index}-tile`}
                    layout={layout}
                    moduleName={title}
                    parsedParameters={parsedParameters}
                    row={row}
                    tile={tile}
                  />
                ) : (
                  <TwoItems
                    historyPush={historyPush}
                    isSwitching={isSwitching}
                    // eslint-disable-next-line react/no-array-index-key
                    key={`${index}-tile`}
                    layout={layout}
                    moduleName={title}
                    parsedParameters={parsedParameters}
                    row={row}
                    tile={tile}
                  />
                )
              })}
            </SwipeableViews>
          </ul>
        </section>
      )
    )
  }
}

Module.defaultProps = {
  geolocation: {
    latitude: null,
    longitude: null,
  },
}

Module.propTypes = {
  geolocation: PropTypes.shape(),
  historyPush: PropTypes.func.isRequired,
  module: PropTypes.instanceOf(Offers, OffersWithCover).isRequired,
  row: PropTypes.number.isRequired,
  trackAllTilesSeen: PropTypes.func.isRequired,
}

export default Module
