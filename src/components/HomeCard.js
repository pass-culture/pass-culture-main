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
      <NavLink to={navLink}>
        {/* <div className="home-card"> */}
        <div className={classnames('home-card', { 'dotted-card': dottedCard })}>
          <div className="home-card-picture">
              <Icon svg={svg}/>
          </div>
          <div className="home-card-text">
            <h1>{title}</h1>
            <p>{text}</p>
          </div>
        </div>
      </NavLink>
    )
  }
}

export default HomeCard
