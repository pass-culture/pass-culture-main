import React from 'react'
import Icon from '../../../../layout/Icon'
import PropTypes from 'prop-types'

export const ApplicationBanner = ({ applicationId }) => (
  <div className="bi-banner">
    <p>
      {'Votre dossier est en cours pour ce lieu'}
    </p>

    <p>
      <a
        className="bi-external-link"
        href={`https://www.demarches-simplifiees.fr/dossiers/${applicationId}`}
        rel="noopener noreferrer"
        target="_blank"
      >
        <Icon
          alt=""
          svg="ico-external-site"
        />
        {'Accéder au dossier'}
      </a>
    </p>
  </div>
)

ApplicationBanner.propTypes = {
  applicationId: PropTypes.string.isRequired,
}
