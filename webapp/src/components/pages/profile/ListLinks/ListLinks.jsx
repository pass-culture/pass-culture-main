import PropTypes from 'prop-types'
import React from 'react'

import ExternalLink from '../ExternalLink/ExternalLink'
import InternalLink from '../InternalLink/InternalLink'
import { signOut } from '../repository/signOut'
import SignOutLinkContainer from '../SignOutLink/SignOutLinkContainer'

const contactUrl = 'https://aide.passculture.app/collections/2834459-beneficiaires'

const ListLinks = ({ historyPush }) => (
  <section className="list-links pf-section">
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
        <SignOutLinkContainer
          historyPush={historyPush}
          signOut={signOut}
        />
      </li>
    </ul>
  </section>
)

ListLinks.propTypes = {
  historyPush: PropTypes.func.isRequired,
}

export default ListLinks
