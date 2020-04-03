import React from 'react'

import Icon from '../../layout/Icon/Icon'

const NON_BREAKING_SPACE = '\u00A0'

const Tutorials = () => (
  <main className="tutorials">
    <Icon
      className="calendar"
      svg="calendar"
    />
    <p className="first-tutorial-text">
      {'À partir d’aujourd’hui, tu as '}
      <span className="text-highlight text-2-ans">
        {`2${NON_BREAKING_SPACE}ans`}
      </span>
      {' et '}
      <span className="text-highlight text-500-euros">
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
  </main>
)

export default Tutorials
