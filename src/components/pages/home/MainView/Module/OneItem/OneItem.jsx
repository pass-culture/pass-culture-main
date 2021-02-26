import PropTypes from 'prop-types'
import React from 'react'

import Cover from '../Cover/Cover'
import OfferTile from '../OfferTile/OfferTile'
import SeeMore from '../SeeMore/SeeMore'

const OneItem = ({
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
  const tileIsACoverItem = typeof tile === 'string'
  const tileIsASeeMoreItem = typeof tile === 'boolean'

  if (tileIsACoverItem) {
    return (
      <Cover
        img={tile}
        key={`${row}-cover`}
        layout={layout}
      />
    )
  } else {
    return tileIsASeeMoreItem ? (
      <SeeMore
        historyPush={historyPush}
        isInFirstModule={row === 0}
        isSwitching={isSwitching}
        key={`${row}-see-more`}
        layout={layout}
        parameters={parsedParameters}
        trackClickSeeMore={trackClickSeeMore}
      />
    ) : (
      <OfferTile
        historyPush={historyPush}
        hit={tile}
        isSwitching={isSwitching}
        key={`${row}${tile.offer.id}`}
        layout={layout}
        moduleName={moduleName}
        trackConsultOffer={trackConsultOffer}
      />
    )
  }
}

OneItem.propTypes = {
  historyPush: PropTypes.func.isRequired,
  isSwitching: PropTypes.bool.isRequired,
  layout: PropTypes.string.isRequired,
  moduleName: PropTypes.string.isRequired,
  parsedParameters: PropTypes.shape().isRequired,
  row: PropTypes.number.isRequired,
  tile: PropTypes.oneOfType([PropTypes.string, PropTypes.bool, PropTypes.shape()]).isRequired,
  trackClickSeeMore: PropTypes.func,
  trackConsultOffer: PropTypes.func.isRequired,
}

export default OneItem
