import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../layout/Icon'

const MyFavorite = ({
  humanizeRelativeDistance,
  name,
  offerTypeLabel,
  status,
  versoUrl,
  thumbUrl,
}) => (
  <li className="mf-my-favorite">
    <Link
      className="teaser-link"
      to={versoUrl}
    >
      <div className="teaser-thumb">{thumbUrl && <img
        alt=""
        src={thumbUrl}
                                                 />}
      </div>
      <div className="teaser-wrapper mf-wrapper">
        <div className="teaser-title">{name}</div>
        <div className="teaser-sub-title">{offerTypeLabel}</div>
        <div className="mf-infos">
          {status && <span className={`mf-status mf-${status.class}`}>{status.label}</span>}
          <span className="teaser-sub-title">{humanizeRelativeDistance}</span>
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
  status: null,
  thumbUrl: null,
}

MyFavorite.propTypes = {
  humanizeRelativeDistance: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  offerTypeLabel: PropTypes.string.isRequired,
  status: PropTypes.shape(),
  thumbUrl: PropTypes.string,
  versoUrl: PropTypes.string.isRequired,
}

export default MyFavorite
