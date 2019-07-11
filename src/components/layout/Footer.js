import PropTypes from 'prop-types'
import classnames from 'classnames'
import React from 'react'
import { compose } from 'redux'
import { connect } from 'react-redux'
import { Link, withRouter } from 'react-router-dom'
import ProfilePicture from './ProfilePicture'

const Footer = ({
  borderTop,
  colored,
  areDetailsVisible,
  id,
  location,
  onTop,
}) => {
  const maybeColored = {}
  if (colored) {
    maybeColored.colored = 'colored'
  }
  const style = {}
  if (!colored) {
    style.display = areDetailsVisible ? 'none' : 'block'
  }
  const className = classnames('footer', {
    bordered: borderTop,
    colored,
    'on-top': onTop,
  })

  const cleanPath = location.pathname.replace(/\/$/, '')
  const menuUrl = `${cleanPath}/menu${location.search}`
  const footerProps = { className, style }
  if (id) {
    footerProps.id = id
  }
  return (
    <footer {...footerProps}>
      <div className="button-wrapper flex-center">
        <Link
          className="profile-button is-block text-center"
          style={{ paddingTop: '0.4rem' }}
          to={menuUrl}
        >
          <ProfilePicture
            alt="Mon menu"
            {...maybeColored}
          />
        </Link>
      </div>
    </footer>
  )
}

Footer.defaultProps = {
  colored: false,
  id: null,
  onTop: false,
}

Footer.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  borderTop: PropTypes.bool.isRequired,
  colored: PropTypes.bool,
  id: PropTypes.string,
  location: PropTypes.shape().isRequired,
  onTop: PropTypes.bool,
}

const mapStateToProps = state => ({
  areDetailsVisible: state.card.areDetailsVisible,
})

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Footer)
