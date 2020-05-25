import PropTypes from 'prop-types'
import React, { Fragment } from 'react'
import HeaderContainer from '../../../layout/Header/HeaderContainer'
import Icon from '../../../layout/Icon/Icon'
import { getAccountDeletionEmail } from '../utils/utils'

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
            <a
              href={termsAndConditionsUrl}
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
              href={gdprUrl}
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
              <Icon svg="ico-delete-account" />
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
