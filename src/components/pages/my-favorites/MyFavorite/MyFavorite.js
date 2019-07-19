import PropTypes from 'prop-types'
import React from 'react'
import { Link } from 'react-router-dom'
import Icon from "../../../layout/Icon";

const MyFavorite = ({ name, type, dateInfos, distance, isFinished, isBooked, isFullyBooked, relativeDate, offerVersoUrl, thumbUrl }) => {
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
            <div className="mf-title">{name}</div>
            <div className="mf-type">{type}</div>
            <div className="mf-date-distance">
              {isFinished &&
                <span className="mf-eneded">TERMINE</span>
              }
              {isBooked &&
                <span className="mf-booked">RESERVE</span>
              }
              { isFullyBooked &&
                <span className="mf-fully-booked">EPUISE</span>
              }
              {relativeDate &&
                <span className="mf-relative-date">{relativeDate}</span>
              }
              <span className="mf-distance">{distance}</span>
            </div>
          </div>
        </div>
        <div className="mf-arrow">
          <Icon
            className="mf-arrow-img"
            svg="ico-next-S"
          />
        </div>
      </Link>
    </li>
  )
}

MyFavorite.defaultProps = {
  thumbUrl: null,
}

MyFavorite.propTypes = {
  name: PropTypes.string.isRequired,
  type: PropTypes.string.isRequired,
  offerVersoUrl: PropTypes.string.isRequired,
  thumbUrl: PropTypes.string,
}

export default MyFavorite
