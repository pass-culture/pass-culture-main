import React from 'react'

import Icon from '../../../layout/Icon/Icon'
import { NON_BREAKING_SPACE } from '../../../../utils/specialCharacters'

const ThirdTutorial = () => (
  <div className="third-tutorial">
    <Icon
      className="icon"
      svg="icon-balance"
    />
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
    <p className="third-tutorial-text second-paragraph">
      {'Aucune limite sur la réservation de '}
      <span className="text-highlight text-go-out text-second-highlight">
        {'sorties'}
      </span>
      {' (concerts, spectacles…) !'}
    </p>
  </div>
)

export default ThirdTutorial
