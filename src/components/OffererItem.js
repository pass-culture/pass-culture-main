import React from 'react'
import { NavLink } from 'react-router-dom'

import { THUMBS_URL } from '../utils/config'

const OffererItem = ({
  id,
  name,
  venue
}) => {
  const src = `${THUMBS_URL}/venues/${venue.id}`
  return (
    <article className="offerer-item media box">
      <figure className="media-left">
        <div className="image is-64x64" style={{
          backgroundImage: `url('${src}')`,
          backgroundSize: 'cover'
        }} />
      </figure>
      <div className="media-content">
        <div className="content">
          <p className="title">
            <strong>{name}</strong>
          </p>
          <p className="subtitle">
            {venue.address}
          </p>
        </div>
        <nav className="level">
          <NavLink to={`/gestion/${id}`}>
            <button className="button is-primary level-item">
              Voir
            </button>
          </NavLink>
        </nav>
      </div>
    </article>
  )
}

export default OffererItem
