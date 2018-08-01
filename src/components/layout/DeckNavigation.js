import React from 'react'
import PropTypes from 'prop-types'

import { ROOT_PATH } from '../../utils/config'
import Icon from './Icon'
import Clue from '../Clue'

const DeckNavigation = ({
  flipHandler,
  handleGoNext,
  handleGoPrevious,
  currentHeaderColor,
}) => {
  const backgroundGradient = `linear-gradient(to bottom, rgba(0,0,0,0) 0%,${currentHeaderColor} 30%,${currentHeaderColor} 100%)`
  return (
    <div id="deck-navigation" style={{ background: backgroundGradient }}>
      <div
        className="controls flex-columns wrap-3"
        style={{ backgroundImage: `url('${ROOT_PATH}/mosaic-w@2x.png')` }}
      >
        {/* previous button */}
        {(handleGoPrevious && (
          <button
            type="button"
            className="button before"
            onClick={handleGoPrevious}
          >
            <Icon svg="ico-prev-w-group" alt="Précédent" />
          </button>
        )) || <span />}
        {/* flip button */}
        {(flipHandler && (
          <div className="flex-rows">
            <button
              type="button"
              onClick={flipHandler}
              onDragLeave={flipHandler}
              className="button to-recto"
            >
              <Icon svg="ico-slideup-w" alt="Plus d'infos" />
            </button>
            <Clue />
          </div>
        )) || <span />}
        {/* next button */}
        {(handleGoNext && (
          <button type="button" className="button after" onClick={handleGoNext}>
            <Icon svg="ico-next-w-group" alt="Suivant" />
          </button>
        )) || <span />}
      </div>
    </div>
  )
}

DeckNavigation.defaultProps = {
  flipHandler: null,
  handleGoNext: null,
  handleGoPrevious: null,
  currentHeaderColor: '#000',
}

DeckNavigation.propTypes = {
  flipHandler: PropTypes.func,
  handleGoNext: PropTypes.func,
  handleGoPrevious: PropTypes.func,
  currentHeaderColor: PropTypes.string,
}

export default DeckNavigation
