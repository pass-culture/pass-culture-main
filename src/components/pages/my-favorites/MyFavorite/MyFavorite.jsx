import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { Link } from 'react-router-dom'

import Icon from '../../../layout/Icon'

class MyFavorite extends Component {
  renderFavorite = () => {
    const {
      date,
      handleToggleFavorite,
      humanizeRelativeDistance,
      isEditMode,
      name,
      offerId,
      offerTypeLabel,
      status,
      thumbUrl,
    } = this.props

    return (
      <Fragment>
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
          {isEditMode ? (
            <label className="field-checkbox">
              <input
                className="input teaser-checkbox"
                onClick={handleToggleFavorite(offerId)}
                type="checkbox"
              />
            </label>
          ) : (
            <Icon
              className="teaser-arrow-img"
              svg="ico-next-S"
            />
          )}
        </div>
      </Fragment>
    )
  }

  render() {
    const { detailsUrl, isEditMode } = this.props

    return (
      <li className="mf-my-favorite">
        {isEditMode ? (
          <div className="teaser-link">{this.renderFavorite()}</div>
        ) : (
          <Link
            className="teaser-link"
            to={detailsUrl}
          >
            {this.renderFavorite()}
          </Link>
        )}
      </li>
    )
  }
}

MyFavorite.defaultProps = {
  date: null,
  isEditMode: false,
  status: [],
  thumbUrl: null,
}

MyFavorite.propTypes = {
  date: PropTypes.string,
  detailsUrl: PropTypes.string.isRequired,
  handleToggleFavorite: PropTypes.func.isRequired,
  humanizeRelativeDistance: PropTypes.string.isRequired,
  isEditMode: PropTypes.bool,
  name: PropTypes.string.isRequired,
  offerId: PropTypes.string.isRequired,
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
