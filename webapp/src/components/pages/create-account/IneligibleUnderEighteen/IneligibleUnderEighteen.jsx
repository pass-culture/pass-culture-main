import React from 'react'
import { Link } from 'react-router-dom'
import { Animation } from '../Animation/Animation'

const IneligibleUnderEighteen = () => {

  return (
    <main className="ineligible-page">
      <div className="animation-text-container">
        <Animation
          name="ineligible-under-eighteen-animation"
          speed={0.7}
        />
        <h2>
          {'Oh non !'}
        </h2>
        <div className="ineligible-text">
          {'Il est encore un peu tôt pour toi. Pour profiter du pass Culture, tu dois avoir 18 ans.'}
        </div>
      </div>
      <div className="link-container">
        <Link
          className="ineligible-back"
          to="/beta"
        >
          {'Retourner à l’accueil'}
        </Link>
      </div>
    </main>
  )
}

export default IneligibleUnderEighteen
