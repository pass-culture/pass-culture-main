/*
 * @debt complexity "Gaël: file nested too deep in directory structure"
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 */

import PropTypes from 'prop-types'
import React from 'react'

import { Banner } from 'ui-kit'

export const ApplicationBanner = ({ applicationId }) => (
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
