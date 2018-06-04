import React from 'react'
import { NavLink } from 'react-router-dom'

import { THUMBS_URL } from '../utils/config'
import { collectionToPath } from '../utils/translate'

const OffererItem = ({
  address,
  id,
  name
}) => {
  const src = `${THUMBS_URL}/structures/${id}`
  return (
    <article className="offerer-item media">
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
            {address}
          </p>
        </div>
        <nav className="level">
          <NavLink to={`/structures/${id}`}>
            <button className="button is-primary level-item">
              Configurer
            </button>
          </NavLink>
        </nav>
      </div>
    </article>
  )
}

export default OffererItem
