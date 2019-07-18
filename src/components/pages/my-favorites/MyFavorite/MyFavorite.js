import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

const MyFavorite = ({ name, offerVersoUrl, thumbUrl }) => {
  return (
    <li className="mf-my-favorite">
      <Link className="mf-link"
            to={offerVersoUrl}>
        <div className="mf-thumb">
          {
            thumbUrl && <img alt="" src={thumbUrl}/>
          }
        </div>
        <div className="mf-infos">
          <div className="mf-heading">
            <div className="mf-name">{name}</div>
          </div>
        </div>
      </Link>
    </li>
  )
}

MyFavorite.defaultProps = {
  stringifyDate: 'Permanent',
  thumbUrl: null,
}

MyFavorite.propTypes = {
  name: PropTypes.string.isRequired,
  offerVersoUrl: PropTypes.string.isRequired,
  thumbUrl: PropTypes.string,
}

export default MyFavorite
