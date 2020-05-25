import React from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import Icon from '../../../layout/Icon/Icon'
import SignoutLinkContainer from '../SignoutLink/SignoutLinkContainer'

const contactUrl = 'https://aide.passculture.app/fr/category/18-ans-1dnil5r/'

const ListLinks = ({ historyPush, readRecommendations }) => (
  <section className="list-links profile-section">
    <ul>
      <li>
        <Link to="/profil/informations">
          <Icon svg="ico-informations" />
          <div className="list-link-label">
            {'Informations personnelles'}
          </div>
          <Icon svg="ico-next-lightgrey" />
        </Link>
      </li>
      <li>
        <Link to="/profil/mot-de-passe">
          <Icon svg="ico-lock" />
          <div className="list-link-label">
            {'Mot de passe'}
          </div>
          <Icon svg="ico-next-lightgrey" />
        </Link>
      </li>
      <li>
        <a
          href={contactUrl}
          rel="noopener noreferrer"
          target="_blank"
          title="Ouverture de l’aide dans une nouvelle fenêtre"
        >
          <Icon svg="ico-help" />
          <div className="list-link-label">
            {'Aide'}
          </div>
          <Icon svg="ico-next-lightgrey" />
        </a>
      </li>
      <li>
        <Link to="/profil/mentions-legales">
          <Icon svg="ico-legal-notice" />
          <div className="list-link-label">
            {'Mentions légales'}
          </div>
          <Icon svg="ico-next-lightgrey" />
        </Link>
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
