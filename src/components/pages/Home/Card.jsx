import React from 'react'
import { NavLink } from 'react-router-dom'

import Icon from '../../layout/Icon'

const Card = ({ svg, title, text, navLink }) => (
  <NavLink
    className="home-card column"
    to={navLink}
  >
    <Icon svg={svg} />
    <div className="home-card-text">
      <h1 className="title is-1 is-spaced">{title}</h1>
      <p className="subtitle is-2">{text}</p>
    </div>
  </NavLink>
)

export default Card
