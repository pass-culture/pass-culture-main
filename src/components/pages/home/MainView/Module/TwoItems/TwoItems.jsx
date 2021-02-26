import PropTypes from 'prop-types'
import Cover from '../Cover/Cover'
import React from 'react'
import OfferTile from '../OfferTile/OfferTile'
import SeeMore from '../SeeMore/SeeMore'

const TwoItems = ({
  historyPush,
  isSwitching,
  layout,
  parsedParameters,
  row,
  tile,
  trackConsultOffer,
  trackClickSeeMore,
  moduleName,
}) => {
  const firstTileIsACoverItem = typeof tile[0] === 'string'
  const firstTileIsASeeMoreItem = typeof tile[0] === 'boolean'
  const offersArePaired = tile.length === 2

  if (firstTileIsACoverItem) {
    return (
      <Cover
        img={tile[0]}
        key={`${row}-cover`}
        layout={layout}
      />
    )
  } else if (firstTileIsASeeMoreItem) {
    return (
      <SeeMore
        historyPush={historyPush}
        isInFirstModule={row === 0}
        isSwitching={isSwitching}
        key={`${row}-see-more`}
        layout={layout}
        parameters={parsedParameters}
        trackClickSeeMore={trackClickSeeMore}
      />
    )
  } else {
    const secondTileIsASeeMoreItem = typeof tile[1] === 'boolean'
    return (
      <div className="ofw-two-tiles-wrapper">
        <OfferTile
          historyPush={historyPush}
          hit={tile[0]}
          isSwitching={isSwitching}
          key={`${row}${tile[0].offer.id}`}
          layout={layout}
          moduleName={moduleName}
          trackConsultOffer={trackConsultOffer}
        />
        {secondTileIsASeeMoreItem ? (
          <SeeMore
            historyPush={historyPush}
            isSwitching={isSwitching}
            key={`${row}-see-more`}
            layout={layout}
            parameters={parsedParameters}
            trackClickSeeMore={trackClickSeeMore}
          />
        ) : offersArePaired ? (
          <OfferTile
            historyPush={historyPush}
            hit={tile[1]}
            isSwitching={isSwitching}
            key={`${row}${tile[1].offer.id}`}
            layout={layout}
            moduleName={moduleName}
            trackConsultOffer={trackConsultOffer}
          />
        ) : null}
      </div>
    )
  }
}

TwoItems.propTypes = {
  historyPush: PropTypes.func.isRequired,
  isSwitching: PropTypes.bool.isRequired,
  layout: PropTypes.string.isRequired,
  moduleName: PropTypes.string.isRequired,
  parsedParameters: PropTypes.shape().isRequired,
  row: PropTypes.number.isRequired,
  tile: PropTypes.arrayOf(
    PropTypes.oneOfType([PropTypes.string, PropTypes.bool, PropTypes.shape()])
  ).isRequired,
  trackClickSeeMore: PropTypes.func,
  trackConsultOffer: PropTypes.func.isRequired,
}

export default TwoItems
