import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import Icon from '../../../layout/Icon/Icon'
import { GDPR_URL, TERMS_AND_CONDITIONS_URL } from '../utils/externalLinks'
import { getAccountDeletionEmail } from '../utils/utils'

const LegalNotice = ({ pathToProfile, userEmail, userId }) => {
  const mailToHref = getAccountDeletionEmail(userId, userEmail)

  return (
    <Fragment>
      <HeaderContainer
        backTo={pathToProfile}
        closeTo={null}
        title="Mentions Légales"
      />
      <section className="legal-notice profile-section">
        <ul>
          <li>
            <a
              href={TERMS_AND_CONDITIONS_URL}
              rel="noopener noreferrer"
              target="_blank"
              title="Ouverture des Conditions Générales d’Utilisation dans une nouvelle page"
            >
              <Icon svg="ico-terms-and-conditions" />
              <div className="list-link-label">
                {'Conditions Générales d’Utilisation'}
              </div>
              <Icon svg="ico-next-lightgrey" />
            </a>
          </li>
          <li>
            <a
              href={GDPR_URL}
              rel="noopener noreferrer"
              target="_blank"
              title="Ouverture de la charte de protection des données personnelles dans une nouvelle page"
            >
              <Icon svg="ico-data-protection" />
              <div className="list-link-label">
                {'Charte de protection des données personnelles'}
              </div>
              <Icon svg="ico-next-lightgrey" />
            </a>
          </li>
          <li>
            <a
              href={mailToHref}
              rel="noopener noreferrer"
              target="_blank"
              title="Envoyer un mail à support@passculture.app"
            >
              <Icon svg="ico-data-protection" />
              <div className="list-link-label">
                {'Suppression du compte'}
              </div>
              <Icon svg="ico-next-lightgrey" />
            </a>
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
