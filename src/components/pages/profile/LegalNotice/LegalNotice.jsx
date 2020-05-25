import PropTypes from 'prop-types'
import React, { Fragment } from 'react'

import { getAccountDeletionEmail } from '../utils/utils'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import ExternalLink from '../ExternalLink/ExternalLink'

const LegalNotice = ({ pathToProfile, userEmail, userId }) => {
  const mailToHref = getAccountDeletionEmail(userId, userEmail)
  const termsAndConditionsUrl =
    'https://docs.passculture.app/textes-normatifs/mentions-legales-et-conditions-generales-dutilisation-de-lapplication-pass-culture'
  const gdprUrl = 'https://docs.passculture.app/textes-normatifs/charte-des-donnees-personnelles'

  return (
    <Fragment>
      <HeaderContainer
        backTo={pathToProfile}
        closeTo={null}
        title="Mentions Légales"
      />
      <section className="list-links profile-section">
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
              title="Envoyer un mail à support@passculture.app"
            />
          </li>
        </ul>
      </section>
    </Fragment>
  )
}

LegalNotice.propTypes = {
  pathToProfile: PropTypes.string.isRequired,
  userEmail: PropTypes.string.isRequired,
  userId: PropTypes.string.isRequired,
}

export default LegalNotice
