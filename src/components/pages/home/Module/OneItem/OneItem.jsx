import PropTypes from 'prop-types'
import Cover from '../Cover/Cover'
import React from 'react'
import SeeMore from '../SeeMore/SeeMore'
import OfferTile from '../OfferTile/OfferTile'

const OneItem = ({ historyPush, isSwitching, layout, parsedParameters, row, tile }) => {
  const tileIsACoverItem = typeof tile === "string"
  const tileIsASeeMoreItem = typeof tile === "boolean"

  if (tileIsACoverItem) {
    return (
      <Cover
        img={tile}
        key={`${row}-cover`}
        layout={layout}
      />
    )
  } else {
    return tileIsASeeMoreItem ?
      <SeeMore
        historyPush={historyPush}
        isSwitching={isSwitching}
        key={`${row}-see-more`}
        layout={layout}
        parameters={parsedParameters}
      /> :
      <OfferTile
        historyPush={historyPush}
        hit={tile}
        isSwitching={isSwitching}
        key={`${row}${tile.offer.id}`}
        layout={layout}
      />
  }
}

OneItem.propTypes = {
  historyPush: PropTypes.func.isRequired,
  isSwitching: PropTypes.bool.isRequired,
  layout: PropTypes.string.isRequired,
  parsedParameters: PropTypes.string.isRequired,
  row: PropTypes.number.isRequired,
  tile: PropTypes.shape().isRequired,
}

export default OneItem
