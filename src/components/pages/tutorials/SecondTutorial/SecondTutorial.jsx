import Icon from '../../../layout/Icon/Icon'
import React from 'react'

const NON_BREAKING_SPACE = '\u00A0'
const NON_BREAKING_HYPHEN = '\u2011'

const SecondTutorial = () => (
  <div className="second-tutorial">
    <Icon
      className="icon"
      svg="icon-ticket"
    />
    <p className="second-tutorial-text">
      {'Profite de ces 500€ '}
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

export default SecondTutorial
