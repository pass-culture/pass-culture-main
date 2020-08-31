import PropTypes from 'prop-types'
import React from 'react'

import ExternalLink from '../ExternalLink/ExternalLink'
import InternalLink from '../InternalLink/InternalLink'
import { signOut } from '../repository/signOut'
import { updateReadRecommendations } from '../repository/updateReadRecommendations'
import SignOutLinkContainer from '../SignOutLink/SignOutLinkContainer'

const contactUrl = 'https://aide.passculture.app/fr/category/18-ans-1dnil5r/'

const ListLinks = ({ historyPush }) => (
  <section className="list-links pf-section">
    <ul>
      <li>
        <InternalLink
          icon="ico-informations"
          label="Informations personnelles"
          to="/accueil/profil/informations"
        />
      </li>
      <li>
        <InternalLink
          icon="ico-lock"
          label="Mot de passe"
          to="/accueil/profil/mot-de-passe"
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
          to="/accueil/profil/mentions-legales"
        />
      </li>
      <li>
        <SignOutLinkContainer
          historyPush={historyPush}
          signOut={signOut}
          updateReadRecommendations={updateReadRecommendations}
        />
      </li>
    </ul>
  </section>
)

ListLinks.propTypes = {
  historyPush: PropTypes.func.isRequired,
}

export default ListLinks
