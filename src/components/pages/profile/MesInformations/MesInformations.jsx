import React from 'react'
import { Link } from 'react-router-dom'

const MesInformations = () => (
  <section>
    <Link
      className="mi-link"
      to="/profil/informations"
    >
      <img
        alt=""
        src="/icons/ico-informations.svg"
      />
      <div className="mi-link-label">
        {'Informations personnelles'}
      </div>
      <img
        alt=""
        src="/icons/ico-next-lightgrey.svg"
      />
    </Link>
    <Link
      className="mi-link"
      to="/profil/password"
    >
      <img
        alt=""
        src="/icons/ico-lock.svg"
      />
      <div className="mi-link-label">
        {'Mot de passe'}
      </div>
      <img
        alt=""
        src="/icons/ico-next-lightgrey.svg"
      />
    </Link>
  </section>
)

export default MesInformations
