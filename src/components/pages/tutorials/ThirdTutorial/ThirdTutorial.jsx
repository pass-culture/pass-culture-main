import Icon from '../../../layout/Icon/Icon'
import React from 'react'

const NON_BREAKING_SPACE = '\u00A0'

const ThirdTutorial = () => (
  <div className="third-tutorial">
    <Icon
      className="icon"
      svg="icon-balance"
    />
    <p className="third-tutorial-text">
      {'Tu peux utiliser jusqu’à 200€ en '}
      <span className="text-highlight text-physical-offer text-first-highlight">
        {`biens${NON_BREAKING_SPACE}physiques`}
      </span>
      {'(livres, vinyles…) et jusqu’à 200€ en'}
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
