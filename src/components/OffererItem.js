import React from 'react'
import { NavLink } from 'react-router-dom'

import { THUMBS_URL } from '../utils/config'
import { collectionToPath } from '../utils/translate'

const OffererItem = ({
  offerer: {
    id,
    address,
    name,
    isActive,
  }
}) => {
  return (
    <article className="offerer-item media">
      <div className="media-content">
        <div className="content">
          <p className="title is-size-2 has-text-weight-bold">{name}</p>
          <p className="subtitle">{address}</p>
          <p className="is-size-small has-text-grey is-italic">{isActive ? 'Activée' : 'En attente de validation'}</p>
        </div>
      </div>
      <div className="media-right">
        <NavLink to={`/structures/${id}`} className="button is-primary is-outlined level-item">
          Configurer
        </NavLink>
      </div>
    </article>
  )
}

export default OffererItem
