import PropTypes from 'prop-types'
import React from 'react'
import { NavLink } from 'react-router-dom'

const Card = ({ SvgElement, title, text, navLink }) => (
  <NavLink className="home-card column" to={navLink}>
    <SvgElement />
    <div className="home-card-text">
      <h1>{title}</h1>
      <p>{text}</p>
    </div>
  </NavLink>
)

Card.propTypes = {
  SvgElement: PropTypes.elementType.isRequired,
  navLink: PropTypes.string.isRequired,
  text: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
}

export default Card
