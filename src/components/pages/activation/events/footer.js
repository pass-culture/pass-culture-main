import React from 'react'
import { Link } from 'react-router-dom'

const ActivationEventsFooter = () => (
  <footer className="flex-0 text-center mb24">
    <Link to="/decouverte" title="Continuer sans activer mon pass Culture">
      <span className="fs16 is-white-text">
        Pas maintenant, je jette un oeil d&apos;abord.
      </span>
    </Link>
  </footer>
)

export default ActivationEventsFooter
