import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'
import Icon from '../../layout/Icon/Icon'

const NotMatch = props => {
  const { redirect } = props
  return (
    <div className="not-match">
      <Icon svg="404" />
      <span className="title">
        {'Oh non !'}
      </span>
      <span className="subtitle">
        {"Cette page n'existe pas"}
      </span>
      <Link
        className="redirection-link"
        to={redirect}
      >
        {'Retour'}
      </Link>
    </div>
  )
}

NotMatch.defaultProps = {
  redirect: '/',
}

NotMatch.propTypes = {
  redirect: PropTypes.string,
}

export default NotMatch
