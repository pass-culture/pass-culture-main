import React from 'react'

import { NON_BREAKING_SPACE } from '../../../../utils/specialCharacters'
import Icon from '../../../layout/Icon/Icon'

const FirstTutorial = () => (
  <div className="first-tutorial">
    <Icon
      className="icon"
      svg="icon-calendar"
    />
    <p className="first-tutorial-text">
      {'À partir d’aujourd’hui, tu as '}
      <span className="text-highlight text-first-highlight">
        {`2${NON_BREAKING_SPACE}ans`}
      </span>
      {' et '}
      <span className="text-highlight text-second-highlight">
        {`500${NON_BREAKING_SPACE}€`}
      </span>
      {
        ' crédités directement sur l’appli pour découvrir de nouvelles activités culturelles autour de chez toi et partout en France !'
      }
    </p>
  </div>
)

export default FirstTutorial
