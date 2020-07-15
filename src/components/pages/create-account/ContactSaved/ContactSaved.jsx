import React, { useState } from 'react'
import { Redirect } from 'react-router'
import { Animation } from '../Animation/Animation'

const ContactSaved = () => {
  const [shouldRedirect, setShouldRedirect] = useState(false)
  const timeBeforeRedirectionToHomepage = 5000

  setTimeout(() => {
    setShouldRedirect(true)
  }, timeBeforeRedirectionToHomepage)

  return shouldRedirect ? (
    <Redirect to="/beta" />
  ) : (
    <main className="contact-saved-page">
      <div className="animation-text-container">
        <Animation
          name="contact-saved-animation"
          speed={0.7}
        />
        <h2>
          {'C’est noté !'}
        </h2>
      </div>
      <div className="redirect-information">
        {'Tu vas être redirigé dans 5 secondes...'}
      </div>
    </main>
  )
}

export default ContactSaved
