import React from 'react'
import {Link} from 'react-router-dom'

import Icon from '../../../layout/Icon/Icon'

const ListLinks = () => (
  <section className="list-links pm-section">
    <ul>
      <li>
        <Link
          to="/profil/informations"
        >
          <Icon svg="ico-informations" />
          <div className="list-link-label">
            {'Informations personnelles'}
          </div>
          <Icon svg="ico-next-lightgrey" />
        </Link>
      </li>
      <li>
        <Link
          to="/profil/password"
        >
          <Icon svg="ico-lock" />
          <div className="list-link-label">
            {'Mot de passe'}
          </div>
          <Icon svg="ico-next-lightgrey" />
        </Link>
      </li>
    </ul>
  </section>
)

export default ListLinks
