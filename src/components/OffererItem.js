import React from 'react'
import { NavLink } from 'react-router-dom'

import { THUMBS_URL } from '../utils/config'
import { collectionToPath } from '../utils/translate'
import Icon from './layout/Icon'


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
          <NavLink to={`/structures/${id}`}>
            <p className="title is-size-2 has-text-weight-bold">{name}</p>
          </NavLink>
          <p className="subtitle">{address}</p>
          <p className="is-size-small has-text-grey is-italic">{isActive ? 'Activée' : 'En attente de validation'}</p>
        </div>
      </div>
      <div className="media-right next-button">
        <NavLink to={`/structures/${id}`}>
          <Icon svg='ico-next-S' />
        </NavLink>
      </div>
    </article>
  )
}

export default OffererItem
