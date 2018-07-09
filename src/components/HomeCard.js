import React, { Component } from 'react'
import { NavLink } from 'react-router-dom'

import Icon from './layout/Icon'

class HomeCard extends Component {
  render() {
    const {
      svg,
      title,
      text,
      navLink,
    } = this.props

    return(
      <NavLink to={navLink} className='home-card column'>
        <Icon svg={svg}/>
        <div className="home-card-text">
          <h1 className='title is-1 is-spaced'>{title}</h1>
          <p className='subtitle is-2'>{text}</p>
        </div>
      </NavLink>
    )
  }
}

export default HomeCard
