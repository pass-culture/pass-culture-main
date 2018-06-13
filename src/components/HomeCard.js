import React, { Component } from 'react'
import Icon from './layout/Icon'
import { NavLink } from 'react-router-dom'

class HomeCard extends Component {
  render() {
    const {
      svg,
      title,
      text,
      navLink
    } = this.props

    return(
      <NavLink to={navLink}>
        <div className="home-card">
          <Icon svg={svg} className="home-card-picture"/>
          <h1>{title}</h1>
          <p>{text}</p>
        </div>
      </NavLink>
    )
  }
}

export default HomeCard
