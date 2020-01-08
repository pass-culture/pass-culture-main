import PropTypes from 'prop-types'
import React, { PureComponent, Fragment } from 'react'
import { Link } from 'react-router-dom'
import Icon from '../Icon/Icon'
import { DEFAULT_THUMB_URL } from '../../../utils/thumb'

class Teaser extends PureComponent {
  renderTeaser = () => {
    const {
      date,
      handleToggleTeaser,
      humanizeRelativeDistance,
      isEditMode,
      name,
      offerId,
      offerTypeLabel,
      statuses,
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
        <div className="teaser-wrapper">
          <div className="teaser-title">
            {name}
          </div>
          <div className="teaser-sub-title">
            {offerTypeLabel}
          </div>
          {date && <div className="teaser-date">
            {date}
          </div>}
          <div className="teaser-infos">
            {statuses.length > 0 &&
              statuses.map(status => (
                <span
                  className={`teaser-status teaser-${status.class}`}
                  key={status.class}
                >
                  {status.label}
                </span>
              ))}
            <span className="teaser-distance">
              {humanizeRelativeDistance}
            </span>
          </div>
        </div>
        <div className="teaser-arrow">
          {isEditMode ? (
            <label className="field-checkbox">
              <input
                className="input teaser-checkbox form-checkbox"
                onClick={handleToggleTeaser(offerId)}
                type="checkbox"
              />
            </label>
          ) : (
            <Icon
              className="teaser-arrow-img"
              svg="ico-next-pink"
            />
          )}
        </div>
      </Fragment>
    )
  }

  render() {
    const { detailsUrl, isEditMode, trackConsultOffer } = this.props

    return (
      <li className="teaser-item">
        {isEditMode ? (
          <div className="teaser-link">
            {this.renderTeaser()}
          </div>
        ) : (
          <Link
            className="teaser-link"
            onClick={trackConsultOffer}
            to={detailsUrl}
          >
            {this.renderTeaser()}
          </Link>
        )}
      </li>
    )
  }
}

Teaser.defaultProps = {
  date: null,
  handleToggleTeaser: () => {},
  isEditMode: false,
  statuses: [],
  thumbUrl: null,
}

Teaser.propTypes = {
  date: PropTypes.string,
  detailsUrl: PropTypes.string.isRequired,
  handleToggleTeaser: PropTypes.func,
  humanizeRelativeDistance: PropTypes.string.isRequired,
  isEditMode: PropTypes.bool,
  name: PropTypes.string.isRequired,
  offerId: PropTypes.string.isRequired,
  offerTypeLabel: PropTypes.string.isRequired,
  statuses: PropTypes.arrayOf(
    PropTypes.shape({
      class: PropTypes.string,
      label: PropTypes.string,
    }).isRequired
  ),
  thumbUrl: PropTypes.string,
  trackConsultOffer: PropTypes.func.isRequired,
}

export default Teaser
