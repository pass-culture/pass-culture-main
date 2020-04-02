import React from 'react'
import Icon from '../../layout/Icon/Icon'

const Tutorials = () => (
  <main className="tutorials">
    <Icon
      alt="calendrier"
      className="calendar"
      svg="calendar"
    />
    <p className="first-tutorial-text">
      <span>
        {"À partir d'aujourd'hui, tu as "}
      </span>
      <span className="text-highlight text-2-ans">
        {'2'}
        &nbsp;
        {'ans'}
      </span>
      <span>
        {' et '}
      </span>
      <span className="text-highlight text-500-euros">
        {'500€'}
      </span>
      <span>
        {
          ' crédités directement sur l’appli pour découvrir de nouvelles activités culturelles autour de chez toi et partout en France !'
        }
      </span>
    </p>
    <div className="slider-points">
      <div className="slider-point filled" />
      <div className="slider-point" />
      <div className="slider-point" />
    </div>
  </main>
)

export default Tutorials
