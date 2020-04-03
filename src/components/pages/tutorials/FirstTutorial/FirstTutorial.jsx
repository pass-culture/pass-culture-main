import Icon from '../../../layout/Icon/Icon'
import React from 'react'

const NON_BREAKING_SPACE = '\u00A0'

const FirstTutorial = () => (
  <div className="first-tutorial">
    <Icon
      className="icon-calendar"
      svg="icon-calendar"
    />
    <p className="first-tutorial-text">
      {'À partir d’aujourd’hui, tu as '}
      <span className="text-highlight text-first-highlight">
        {`2${NON_BREAKING_SPACE}ans`}
      </span>
      {' et '}
      <span className="text-highlight text-second-highlight">
        {'500€'}
      </span>
      {
        ' crédités directement sur l’appli pour découvrir de nouvelles activités culturelles autour de chez toi et partout en France !'
      }
    </p>
    <div className="slider-points">
      <div className="slider-point filled" />
      <div className="slider-point" />
      <div className="slider-point" />
    </div>
  </div>
)

export default FirstTutorial
