import React from 'react'

import Icon from '../../../layout/Icon/Icon'
import { NON_BREAKING_SPACE } from '../../../../utils/specialCharacters'
import PropTypes from 'prop-types'
import EnteringSides from '../animationsEnteringSides/EnteringSides'
import EnteringSidesClassNames from '../animationsEnteringSides/EnteringSidesClassNames'

const ThirdTutorial = ({ enteringSide, isNewBookingLimitsActived }) => (
  <div className={`third-tutorial ${EnteringSidesClassNames[enteringSide]}`}>
    <Icon
      className="icon"
      svg="icon-balance"
    />
    {!isNewBookingLimitsActived && (
      <p className="third-tutorial-text">
        {`Tu peux utiliser jusqu’à 200${NON_BREAKING_SPACE}€ en `}
        <span className="text-highlight text-physical-offer text-first-highlight">
          {`biens${NON_BREAKING_SPACE}physiques`}
        </span>
        {`(livres, vinyles…) et jusqu’à 200${NON_BREAKING_SPACE}€ en `}
        <span className="text-highlight text-digital-offer text-second-highlight">
          {`biens${NON_BREAKING_SPACE}numériques`}
        </span>
        {' (streaming, jeux vidéo…).'}
      </p>
    )}
    {isNewBookingLimitsActived && (
      <p className="third-tutorial-text">
        {`Tu peux utiliser jusqu’à 100${NON_BREAKING_SPACE}€ en `}
        <span className="text-highlight text-digital-offer text-first-highlight">
          {`biens${NON_BREAKING_SPACE}numériques`}
        </span>
        {' (streaming, jeux vidéo…).'}
      </p>
    )}
    <p className="third-tutorial-text second-paragraph">
      {'Aucune limite sur la réservation de '}
      <span className="text-highlight text-go-out text-second-highlight">
        {'sorties'}
      </span>
      {' (concerts, spectacles…) !'}
    </p>
  </div>
)

ThirdTutorial.propTypes = {
  enteringSide: PropTypes.oneOf(Object.keys(EnteringSides)).isRequired,
  isNewBookingLimitsActived: PropTypes.bool.isRequired,
}

export default ThirdTutorial
