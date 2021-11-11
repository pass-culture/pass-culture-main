import React from 'react'
import PropTypes from 'prop-types'

const VersoActionsBar = ({ url }) => (
  <nav className="verso-actions-bar items-center flex-center flex-columns fs16">
    <a
      className="is-red-text is-bold flex-columns items-center flex-center"
      href={url}
      id="verso-online-booked-button"
      rel="noopener noreferrer"
      target="_blank"
      title="Ouverture de l’offre dans une nouvelle fenêtre"
    >
      <span className="fs16">
        {'Accéder'}
      </span>
    </a>
  </nav>
)

VersoActionsBar.defaultProps = {
  url: null,
}

VersoActionsBar.propTypes = {
  url: PropTypes.string,
}

export default VersoActionsBar
