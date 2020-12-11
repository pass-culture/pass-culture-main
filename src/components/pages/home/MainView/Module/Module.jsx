import PropTypes from 'prop-types'
import React, { useCallback, useState, useRef } from 'react'
import SwipeableViews from 'react-swipeable-views'

import { PANE_LAYOUT } from '../domain/layout'
import Offers from '../domain/ValueObjects/Offers'
import OffersWithCover from '../domain/ValueObjects/OffersWithCover'
import { buildPairedTiles, buildTiles } from './domain/buildTiles'
import OneItem from './OneItem/OneItem'
import TwoItems from './TwoItems/TwoItems'

const swipeRatio = 0.2

const Module = props => {
  const { historyPush, row, module, trackAllTilesSeen, results } = props
  const { algolia, cover, display } = module

  const [isSwitching, setIsSwitching] = useState(false)
  const onSwitching = useCallback(() => setIsSwitching(true), [])
  const onTransitionEnd = useCallback(() => setIsSwitching(false), [])

  const haveAlreadySeenAllTiles = useRef(false)

  const onChangeIndex = useCallback(
    numberOfTiles => index => {
      const { display: { title = 'Missing title' } = {} } = module
      const haveSeenAllTilesForTheFirstTime =
        index + 1 === numberOfTiles && !haveAlreadySeenAllTiles.current

      if (haveSeenAllTilesForTheFirstTime) {
        trackAllTilesSeen(title, numberOfTiles)
        haveAlreadySeenAllTiles.current = true
      }
    },
    [module, trackAllTilesSeen]
  )

  const { layout = PANE_LAYOUT['ONE-ITEM-MEDIUM'], title } = display || {}
  const { hits = [], nbHits = 0, parsedParameters = null } = results || {}
  const isOneItemLayout = layout === PANE_LAYOUT['ONE-ITEM-MEDIUM']
  const tiles = isOneItemLayout
    ? buildTiles({ algolia, cover, hits, nbHits })
    : buildPairedTiles({ algolia, cover, hits, nbHits })

  return (
    <section className="module-wrapper">
      <h1>
        {title}
      </h1>
      <ul>
        <SwipeableViews
          className={layout || PANE_LAYOUT['ONE-ITEM-MEDIUM']}
          disableLazyLoading
          enableMouseEvents
          hysteresis={swipeRatio}
          onChangeIndex={onChangeIndex(tiles.length)}
          onSwitching={onSwitching}
          onTransitionEnd={onTransitionEnd}
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
}

Module.propTypes = {
  historyPush: PropTypes.func.isRequired,
  module: PropTypes.instanceOf(Offers, OffersWithCover).isRequired,
  results: PropTypes.shape({
    hits: PropTypes.arrayOf(PropTypes.shape()).isRequired,
    nbHits: PropTypes.number.isRequired,
    parsedParameters: PropTypes.shape(),
  }).isRequired,
  row: PropTypes.number.isRequired,
  trackAllTilesSeen: PropTypes.func.isRequired,
}

export default Module
