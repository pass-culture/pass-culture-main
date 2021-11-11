import React from 'react'
import { Link } from 'react-router-dom'

import { SUPPORT_EMAIL } from '../../../../utils/config'
import { Animation } from '../Animation/Animation'

const IneligibleOverEighteen = () => (
  <main className="ineligible-over-eighteen-page">
    <div className="animation-text-container">
      <Animation
        name="ineligible-over-eighteen-animation"
        speed={0.7}
      />
      <h1>
        {'Tu as plus de 18 ans'}
      </h1>
      <p>
        {'Seules les personnes dans leur dix-huitième année peuvent déposer un dossier.'}
      </p>
      <p>
        {'N’hésite pas à contacter'}
        <a href={`mailto:${SUPPORT_EMAIL}`}>
          {' notre support, '}
        </a>
        {
          'nous pourrons te conseiller d’autres manières de découvrir la culture près de chez toi !'
        }
      </p>
    </div>
    <div className="link-container">
      <Link
        className="back-home-link"
        to="/beta"
      >
        {'Retourner à l’accueil'}
      </Link>
    </div>
  </main>
)

export default IneligibleOverEighteen
