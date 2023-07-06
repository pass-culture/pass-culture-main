import PropTypes from 'prop-types'
import React from 'react'

import { Banner } from 'ui-kit'

interface ApplicationBannerProps {
  applicationId: string
}

const ApplicationBanner = ({ applicationId }: ApplicationBannerProps) => (
  <Banner
    links={[
      {
        href: `https://www.demarches-simplifiees.fr/dossiers/${applicationId}`,
        linkTitle: 'Voir le dossier en cours',
      },
    ]}
    type="notification-info"
  >
    Les coordonnées bancaires de votre lieu sont en cours de validation par
    notre service financier. <br /> Vos remboursements seront rétroactifs une
    fois vos coordonnées bancaires ajoutées.
  </Banner>
)

ApplicationBanner.propTypes = {
  applicationId: PropTypes.string.isRequired,
}

export default ApplicationBanner
