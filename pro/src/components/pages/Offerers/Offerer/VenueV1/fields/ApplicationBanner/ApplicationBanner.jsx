import PropTypes from 'prop-types'
import React from 'react'

import { Banner } from 'ui-kit'

const ApplicationBanner = ({ applicationId }) => (
  <Banner
    href={`https://www.demarches-simplifiees.fr/dossiers/${applicationId}`}
    linkTitle="Voir le dossier en cours"
    type="notification-info"
  >
    Les coordonnées bancaires de votre lieu sont en cours de validation par
    notre service financier.
  </Banner>
)

ApplicationBanner.propTypes = {
  applicationId: PropTypes.string.isRequired,
}

export default ApplicationBanner
