import PropTypes from 'prop-types'
import React, { Component } from 'react'
import SwipeableViews from 'react-swipeable-views'

import { fetchAlgolia } from '../../../../vendor/algolia/algolia'
import { CONTENTFUL_PARAMETERS, parseAlgoliaParameters } from '../domain/parseAlgoliaParameters'
import Offers from '../domain/ValueObjects/Offers'
import Cover from './Cover/Cover'
import { buildArrayOf } from './domain/buildTiles'
import OfferTile from './OfferTile/OfferTile'
import { PANE_LAYOUT } from '../domain/layout'
import OffersWithCover from '../domain/ValueObjects/OffersWithCover'
import SeeMore from './SeeMore/SeeMore'

class Module extends Component {
  constructor(props) {
    super(props)
    this.state = {
      hits: [],
      isSwitching: false,
      nbHits: 0,
      parsedParameters: null,
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

  onSwitching = () => {
    this.setState({ isSwitching: true })
  }

  onTransitionEnd = () => {
    this.setState({ isSwitching: false })
  }

  renderOneItem = () => {
    const {
      historyPush,
      module: { display },
      row,
    } = this.props
    const { isSwitching, parsedParameters } = this.state
    const tiles = this.buildTiles()

    return (
      tiles.map(tile => {
        const tileIsACoverItem = typeof tile === "string"
        const tileIsASeeMoreItem = typeof tile === "boolean"

        if (tileIsACoverItem) {
          return (
            <Cover
              img={tile}
              key={`${row}-cover`}
              layout={display.layout}
            />
          )
        } else {
          return tileIsASeeMoreItem ?
            <SeeMore
              key={`${row}-see-more`}
              layout={display.layout}
              parameters={parsedParameters}
            /> :
            <OfferTile
              historyPush={historyPush}
              hit={tile}
              isSwitching={isSwitching}
              key={`${row}${tile.offer.id}`}
              layout={display.layout}
            />
        }
      })
    )
  }

  buildTiles = () => {
    const {
      module: { algolia, cover },
    } = this.props
    const { hits, nbHits } = this.state
    const seeMoreOffers = hits.length < nbHits
    const tiles = [...hits]

    if (cover) {
      tiles.unshift(cover)
    }

    const seeMoreTileCanBeDisplayed = !(
      algolia[CONTENTFUL_PARAMETERS.TAGS] ||
      algolia[CONTENTFUL_PARAMETERS.BEGINNING_DATETIME] ||
      algolia[CONTENTFUL_PARAMETERS.ENDING_DATETIME]
    )
    if (seeMoreOffers && seeMoreTileCanBeDisplayed) {
      tiles.push(seeMoreOffers)
    }
    return tiles
  }

  renderTwoItems = () => {
    const {
      historyPush,
      module: { cover, display },
      row,
    } = this.props
    const { hits, isSwitching } = this.state
    const tiles = buildArrayOf({ cover, hits })

    return (
      tiles.map(tile => {
        const firstTileIsACover = !tile[0].offer
        const offersArePaired = tile.length === 2
        return firstTileIsACover ?
          <Cover
            img={tile}
            key={`${row}-cover`}
            layout={display.layout}
          />
          :
          <div className="ofw-two-tiles-wrapper">
            <OfferTile
              historyPush={historyPush}
              hit={tile[0]}
              isSwitching={isSwitching}
              key={`${row}${tile[0].offer.id}`}
              layout={display.layout}
            />
            {offersArePaired && (
              <OfferTile
                historyPush={historyPush}
                hit={tile[1]}
                isSwitching={isSwitching}
                key={`${row}${tile[1].offer.id}`}
                layout={display.layout}
              />)}
          </div>
      }))
  }

  render() {
    const {
      module: { display: { layout, minOffers = 0, title} },
    } = this.props
    const { hits, nbHits } = this.state
    const atLeastOneHit = hits.length > 0
    const minOffersHasBeenReached = nbHits >= minOffers
    const shouldModuleBeDisplayed = atLeastOneHit && minOffersHasBeenReached

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
              onSwitching={this.onSwitching}
              onTransitionEnd={this.onTransitionEnd}
              resistance
              slideClassName="module-slides"
            >
              {layout === PANE_LAYOUT['TWO-ITEMS'] ?
                this.renderTwoItems() :
                this.renderOneItem()}
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
}

export default Module
