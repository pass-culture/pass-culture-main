import React from 'react'
import PropTypes from 'prop-types'

import { NON_BREAKING_SPACE } from '../../../../utils/specialCharacters'
import Icon from '../../../layout/Icon/Icon'
import EnteringSides from '../animationsEnteringSides/EnteringSides'
import EnteringSidesClassNames from '../animationsEnteringSides/EnteringSidesClassNames'

const FirstTutorial = ({ enteringSide, depositAmount }) => (
  <div className={`first-tutorial ${EnteringSidesClassNames[enteringSide]}`}>
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
        {`${depositAmount}${NON_BREAKING_SPACE}€`}
      </span>
      {
        ' crédités directement sur l’appli pour découvrir de nouvelles activités culturelles autour de chez toi et partout en France !'
      }
    </p>
  </div>
)

FirstTutorial.propTypes = {
  depositAmount: PropTypes.number.isRequired,
  enteringSide: PropTypes.oneOf(Object.keys(EnteringSides)).isRequired,
}

export default FirstTutorial
