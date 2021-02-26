import PropTypes from 'prop-types'
import React, { useCallback, useState, useRef } from 'react'
import SwipeableViews from 'react-swipeable-views'

import { PANE_LAYOUT } from '../domain/layout'
import RecommendationPane from '../domain/ValueObjects/RecommendationPane'
import { buildPairedTiles, buildTiles } from './domain/buildTiles'
import OneItem from './OneItem/OneItem'
import TwoItems from './TwoItems/TwoItems'

const swipeRatio = 0.2

const RecommendationModule = props => {
  const { historyPush, row, module, hits } = props
  const { trackAllTilesSeen, trackConsultOffer: consultOffer } = props
  const { display } = module
  const { layout = PANE_LAYOUT['ONE-ITEM-MEDIUM'], title } = display || {}

  const [isSwitching, setIsSwitching] = useState(false)
  const onSwitching = useCallback(() => setIsSwitching(true), [])
  const onTransitionEnd = useCallback(() => setIsSwitching(false), [])

  const haveAlreadySeenAllTiles = useRef(false)

  const onChangeIndex = useCallback(
    numberOfTiles => index => {
      const haveSeenAllTiles = index + 1 === numberOfTiles
      if (haveSeenAllTiles && !haveAlreadySeenAllTiles.current) {
        trackAllTilesSeen(title, numberOfTiles)
        haveAlreadySeenAllTiles.current = true
      }
    },
    [trackAllTilesSeen, title]
  )

  const trackConsultOffer = useCallback(offerId => consultOffer(title, offerId), [
    title,
    consultOffer,
  ])

  const isOneItemLayout = layout === PANE_LAYOUT['ONE-ITEM-MEDIUM']
  const tiles = isOneItemLayout
    ? buildTiles({ algolia: {}, cover: undefined, hits, nbHits: hits.length })
    : buildPairedTiles({ algolia: {}, cover: undefined, hits, nbHits: hits.length })

  const LayoutComponent = isOneItemLayout ? OneItem : TwoItems
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
          {tiles.map((tile, index) => (
            <LayoutComponent
              historyPush={historyPush}
              isSwitching={isSwitching}
              // eslint-disable-next-line react/no-array-index-key
              key={`${index}-tile`}
              layout={layout}
              moduleName={title}
              parsedParameters={{}}
              row={row}
              tile={tile}
              trackConsultOffer={trackConsultOffer}
            />
          ))}
        </SwipeableViews>
      </ul>
    </section>
  )
}

RecommendationModule.propTypes = {
  historyPush: PropTypes.func.isRequired,
  hits: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  module: PropTypes.instanceOf(RecommendationPane).isRequired,
  row: PropTypes.number.isRequired,
  trackAllTilesSeen: PropTypes.func.isRequired,
  trackConsultOffer: PropTypes.func.isRequired,
}

export default RecommendationModule
