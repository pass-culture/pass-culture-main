import { Icon } from 'pass-culture-shared'
import React from 'react'
import { NavLink } from 'react-router-dom'

import OffererItemActions from './OffererItemActions'

const OffererItem = ({ offerer, venues }) => {
  const { id, name, isValidated } = offerer || {}

  const showPath = `/structures/${id}`

  const $actions = isValidated ? (
    <OffererItemActions offerer={offerer} />
  ) : (
    <li className="is-italic">
      Structure en cours de validation par l&apos;équipe Pass Culture.
    </li>
  )

  return (
    <li className="offerer-item">
      <div className="list-content">
        <p className="name">
          <NavLink to={showPath}>{name}</NavLink>
        </p>
        <ul className="actions">{$actions}</ul>
      </div>
      <div className="caret">
        <NavLink to={showPath}>
          <Icon svg="ico-next-S" />
        </NavLink>
      </div>
    </li>
  )
}

export default OffererItem
