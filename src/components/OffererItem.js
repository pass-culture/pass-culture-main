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
  const showPath = `/structures/${id}`
  return (
    <li className="offerer-item">
      <div className='list-content'>
        <p className="name">
          <NavLink to={showPath}>
            {name}
          </NavLink>
        </p>
        <ul className='actions'>
          <li>
            <NavLink to={`/offres?offererId=${id}`} className='has-text-primary'>
              <Icon svg='ico-offres-r' /> ?? offres
            </NavLink>
          </li>
          <li>
            <NavLink to={showPath}>
              <Icon svg='picto-structure' /> ?? lieux
            </NavLink>
          </li>
          <li className='is-italic'>{isActive ? 'Activée' : 'En attente de validation'}</li>
        </ul>
      </div>
      <div className='caret'>
        <NavLink to={showPath}>
          <Icon svg='ico-next-S' />
        </NavLink>
      </div>
    </li>
  )
}

export default OffererItem
