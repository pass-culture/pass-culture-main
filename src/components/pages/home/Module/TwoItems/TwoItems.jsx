import PropTypes from 'prop-types'
import Cover from '../Cover/Cover'
import React from 'react'
import OfferTile from '../OfferTile/OfferTile'
import SeeMoreContainer from '../SeeMore/SeeMoreContainer'

const TwoItems = ({ historyPush, isSwitching, layout, moduleName, parsedParameters, row, tile }) => {
  const firstTileIsACoverItem = typeof tile[0] === "string"
  const firstTileIsASeeMoreItem = typeof tile[0] === "boolean"
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
      <SeeMoreContainer
        historyPush={historyPush}
        isSwitching={isSwitching}
        key={`${row}-see-more`}
        layout={layout}
        parameters={parsedParameters}
      />
    )
  } else {
    const secondTileIsASeeMoreItem = typeof tile[1] === "boolean"
    return (
      <div className="ofw-two-tiles-wrapper">
        <OfferTile
          historyPush={historyPush}
          hit={tile[0]}
          isSwitching={isSwitching}
          key={`${row}${tile[0].offer.id}`}
          layout={layout}
        />
        {secondTileIsASeeMoreItem ?
          <SeeMoreContainer
            historyPush={historyPush}
            isSwitching={isSwitching}
            key={`${row}-see-more`}
            layout={layout}
            moduleName={moduleName}
            parameters={parsedParameters}
          /> :
          offersArePaired ?
            <OfferTile
              historyPush={historyPush}
              hit={tile[1]}
              isSwitching={isSwitching}
              key={`${row}${tile[1].offer.id}`}
              layout={layout}
            /> :
            null}
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
  tile: PropTypes.arrayOf(PropTypes.oneOfType([
    PropTypes.string,
    PropTypes.bool,
    PropTypes.shape(),
  ])).isRequired,
}

export default TwoItems
