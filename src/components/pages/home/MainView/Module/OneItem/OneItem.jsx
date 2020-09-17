import PropTypes from 'prop-types'
import React from 'react'

import Cover from '../Cover/Cover'
import OfferTile from '../OfferTile/OfferTile'
import SeeMoreContainer from '../SeeMore/SeeMoreContainer'

const OneItem = ({ historyPush, isSwitching, layout, moduleName, parsedParameters, row, tile }) => {
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
      <SeeMoreContainer
        historyPush={historyPush}
        isInFirstModule={row === 0}
        isSwitching={isSwitching}
        key={`${row}-see-more`}
        layout={layout}
        moduleName={moduleName}
        parameters={parsedParameters}
      />
    ) : (
      <OfferTile
        historyPush={historyPush}
        hit={tile}
        isSwitching={isSwitching}
        key={`${row}${tile.offer.id}`}
        layout={layout}
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
}

export default OneItem
