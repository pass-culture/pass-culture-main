import React from 'react'

import Icon from '../../../layout/Icon/Icon'
import { NON_BREAKING_SPACE, NON_BREAKING_HYPHEN } from '../../../../utils/specialCharacters'
import PropTypes from 'prop-types'
import EnteringSides from '../animationsEnteringSides/EnteringSides'
import EnteringSidesClassNames from '../animationsEnteringSides/EnteringSidesClassNames'

const SecondTutorial = ({ enteringSide }) => (
  <div className={`second-tutorial ${EnteringSidesClassNames[enteringSide]}`}>
    <Icon
      className="icon"
      svg="icon-ticket"
    />
    <p className="second-tutorial-text">
      {`Profite de ces 500${NON_BREAKING_SPACE}€ `}
      <span className="text-highlight text-book-in-app text-first-highlight">
        {`en${NON_BREAKING_SPACE}réservant${NON_BREAKING_SPACE}sur${NON_BREAKING_SPACE}l’appli`}
      </span>
      {' des concerts, des cours, des abonnements à une plateforme numérique…'}
    </p>
    <p className="second-tutorial-text second-paragraph">
      {'Psst : profite des '}
      <span className="text-highlight text-duo-offer text-second-highlight">
        {`offres${NON_BREAKING_SPACE}duo`}
      </span>
      {` pour inviter un ami, un voisin ou ta grand${NON_BREAKING_HYPHEN}mère !`}
    </p>
  </div>
)

SecondTutorial.propTypes = {
  enteringSide: PropTypes.oneOf(Object.keys(EnteringSides)).isRequired,
}

export default SecondTutorial
