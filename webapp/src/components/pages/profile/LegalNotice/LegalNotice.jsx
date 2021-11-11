import PropTypes from 'prop-types'
import React from 'react'

import HeaderContainer from '../../../layout/Header/HeaderContainer'
import ExternalLink from '../ExternalLink/ExternalLink'
import { SUPPORT_EMAIL } from '../../../../utils/config'
import { getAccountDeletionEmail } from '../domain/getAccountDeletionEmail'

const LegalNotice = ({ pathToProfile, userEmail }) => {
  const mailToHref = getAccountDeletionEmail(userEmail)
  const termsAndConditionsUrl = 'https://pass.culture.fr/cgu/'
  const gdprUrl = 'https://pass.culture.fr/donnees-personnelles/'

  return (
    <main className="pf-container">
      <HeaderContainer
        backTo={pathToProfile}
        title="Mentions Légales"
      />
      <section className="list-links pf-section">
        <ul>
          <li>
            <ExternalLink
              href={termsAndConditionsUrl}
              icon="ico-terms-and-conditions"
              label="Conditions Générales d’Utilisation"
              title="Ouverture des Conditions Générales d’Utilisation dans une nouvelle page"
            />
          </li>
          <li>
            <ExternalLink
              href={gdprUrl}
              icon="ico-data-protection"
              label="Charte de protection des données personnelles"
              title="Ouverture de la charte de protection des données personnelles dans une nouvelle page"
            />
          </li>
          <li>
            <ExternalLink
              href={mailToHref}
              icon="ico-delete-account"
              label="Suppression du compte"
              rel=""
              target=""
              title={`Envoyer un e-mail à ${SUPPORT_EMAIL}`}
            />
          </li>
        </ul>
      </section>
    </main>
  )
}

LegalNotice.propTypes = {
  pathToProfile: PropTypes.string.isRequired,
  userEmail: PropTypes.string.isRequired,
}

export default LegalNotice
