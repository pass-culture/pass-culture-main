import React from 'react'
import PropTypes from 'prop-types'

import SignoutLinkContainer from '../SignoutLink/SignoutLinkContainer'
import ExternalLink from '../ExternalLink/ExternalLink'
import InternalLink from '../InternalLink/InternalLink'

const contactUrl = 'https://aide.passculture.app/fr/category/18-ans-1dnil5r/'

const ListLinks = ({ historyPush, readRecommendations }) => (
  <section className="list-links profile-section">
    <ul>
      <li>
        <InternalLink
          icon="ico-informations"
          label="Informations personnelles"
          to="/profil/informations"
        />
      </li>
      <li>
        <InternalLink
          icon="ico-lock"
          label="Mot de passe"
          to="/profil/mot-de-passe"
        />
      </li>
      <li>
        <ExternalLink
          href={contactUrl}
          icon="ico-help"
          label="Aide"
          title="Ouverture de l’aide dans une nouvelle fenêtre"
        />
      </li>
      <li>
        <InternalLink
          icon="ico-legal-notice"
          label="Mentions légales"
          to="/profil/mentions-legales"
        />
      </li>
      <li>
        <SignoutLinkContainer
          historyPush={historyPush}
          readRecommendations={readRecommendations}
        />
      </li>
    </ul>
  </section>
)

ListLinks.propTypes = {
  historyPush: PropTypes.func.isRequired,
  readRecommendations: PropTypes.arrayOf(PropTypes.object).isRequired,
}

export default ListLinks
