import PropTypes from 'prop-types'
import React, { Component, Fragment } from 'react'
import { Link } from 'react-router-dom'

import { ICONS_URL } from '../../../utils/config'
const DEFAULT_THUMB_URL = `${ICONS_URL}/picto-placeholder-visueloffre.png`
import Icon from '../Icon/Icon'

class Teaser extends Component {
  renderItem = () => {
    const {
      date,
      handleToggleItem,
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
        <div className="teaser-thumb">
          <img
            alt=""
            src={thumbUrl || DEFAULT_THUMB_URL}
          />
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
                onClick={handleToggleItem(offerId)}
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
    const { className, detailsUrl, isEditMode } = this.props

    return (
      <li className={`${className}`}>
        {isEditMode ? (
          <div className="teaser-link">{this.renderItem()}</div>
        ) : (
          <Link
            className="teaser-link"
            to={detailsUrl}
          >
            {this.renderItem()}
          </Link>
        )}
      </li>
    )
  }
}

Teaser.defaultProps = {
  className: '',
  date: null,
  isEditMode: false,
  status: [],
  thumbUrl: null,
}

Teaser.propTypes = {
  className: PropTypes.string,
  date: PropTypes.string,
  detailsUrl: PropTypes.string.isRequired,
  handleToggleItem: PropTypes.func.isRequired,
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

export default Teaser
