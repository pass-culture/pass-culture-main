import PropTypes from 'prop-types'
import React from 'react'

import Banner from 'components/layout/Banner'

export const ApplicationBanner = ({ applicationId }) => (
  <Banner
    href={`https://www.demarches-simplifiees.fr/dossiers/${applicationId}`}
    linkTitle="Accéder au dossier"
    subtitle="Votre dossier est en cours pour ce lieu"
  />
)

ApplicationBanner.propTypes = {
  applicationId: PropTypes.string.isRequired,
}
