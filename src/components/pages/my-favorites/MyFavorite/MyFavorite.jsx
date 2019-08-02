import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../layout/Icon'

const MyFavorite = ({
  date,
  detailsUrl,
  humanizeRelativeDistance,
  name,
  offerTypeLabel,
  status,
  thumbUrl,
}) => (
  <li className="mf-my-favorite">
    <Link
      className="teaser-link"
      to={detailsUrl}
    >
      <div className="teaser-thumb">{thumbUrl && <img
        alt=""
        src={thumbUrl}
                                                 />}
      </div>
      <div className="teaser-wrapper mf-wrapper">
        <div className="teaser-title">{name}</div>
        <div className="teaser-sub-title">{offerTypeLabel}</div>
        {date && <div className="teaser-date">{date}</div>}
        <div className="mf-infos">
          {status.length > 0 &&
            status.map(status => (
              <span
                className={`mf-status mf-${status.class}`}
                key={status.class}
              >
                {status.label}
              </span>
            ))}
          <span className="teaser-distance">{humanizeRelativeDistance}</span>
        </div>
      </div>
      <div className="teaser-arrow">
        <Icon
          className="teaser-arrow-img"
          svg="ico-next-S"
        />
      </div>
    </Link>
  </li>
)

MyFavorite.defaultProps = {
  date: null,
  status: [],
  thumbUrl: null,
}

MyFavorite.propTypes = {
  date: PropTypes.string,
  detailsUrl: PropTypes.string.isRequired,
  humanizeRelativeDistance: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  offerTypeLabel: PropTypes.string.isRequired,
  status: PropTypes.arrayOf(
    PropTypes.shape({
      class: PropTypes.string,
      label: PropTypes.string,
    }).isRequired
  ),
  thumbUrl: PropTypes.string,
}

export default MyFavorite
