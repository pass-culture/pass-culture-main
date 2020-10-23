import React from 'react'
import { NavLink } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import PropTypes from 'prop-types'

const Card = ({ svg, title, text, navLink }) => (
  <NavLink
    className="home-card column"
    to={navLink}
  >
    <Icon svg={svg} />
    <div className="home-card-text">
      <h1 className="title is-1 is-spaced">
        {title}
      </h1>
      <p className="subtitle is-2">
        {text}
      </p>
    </div>
  </NavLink>
)

Card.propTypes = {
  navLink: PropTypes.string.isRequired,
  svg: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
}

export default Card
