import classnames from 'classnames'
import React, { Component } from 'react'
import Icon from './layout/Icon'
import { NavLink } from 'react-router-dom'

class HomeCard extends Component {
  render() {
    const {
      svg,
      title,
      text,
      navLink,
      dottedCard
    } = this.props

    return(
      <NavLink to={navLink} className='home-card column'>
        <Icon svg={svg}/>
        <div className="home-card-text">
          <h1>{title}</h1>
          <p>{text}</p>
        </div>
      </NavLink>
    )
  }
}

export default HomeCard
