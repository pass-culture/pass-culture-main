import React from 'react'
import { Link } from 'react-router-dom'

const InvalidLink = () => (
  <div className="logout-form-container error">
    <div>
      <p className="fs20 mb28">{'Le lien sur lequel vous avez cliqué est invalide.'}</p>
      <Link
        className="no-background border-all rd4 py12 px18 is-inline-block is-white-text text-center fs16"
        to="/connexion"
      >
        {'S’identifier'}
      </Link>
    </div>
  </div>
)
export default InvalidLink
