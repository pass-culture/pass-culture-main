import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../layout/Icon/Icon'

const MesInformations = () => (
  <section>
    <Link
      className="mi-link"
      to="/profil/informations"
    >
      <Icon svg="ico-informations" />
      <div className="mi-link-label">
        {'Informations personnelles'}
      </div>
      <Icon svg="ico-next-lightgrey" />
    </Link>
    <div className="mi-separator" />
    <Link
      className="mi-link"
      to="/profil/password"
    >
      <Icon svg="ico-lock" />
      <div className="mi-link-label">
        {'Mot de passe'}
      </div>
      <Icon svg="ico-next-lightgrey" />
    </Link>
    <div className="mi-separator" />
  </section>
)

export default MesInformations
