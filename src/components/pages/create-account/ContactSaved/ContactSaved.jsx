import React, { useEffect, useState } from 'react'
import { Redirect } from 'react-router'
import { Animation } from '../Animation/Animation'

const ContactSaved = () => {
  const [countDown, setcountDown] = useState(5)

  useEffect(() => {
    const decreaseCountByOneEverySecond = setInterval(() => setcountDown(count => count - 1), 1000)

    return () => clearInterval(decreaseCountByOneEverySecond)
  }, [])

  return countDown === 0 ? (
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
        {`Tu vas être redirigé dans ${countDown} secondes...`}
      </div>
    </main>
  )
}

export default ContactSaved
