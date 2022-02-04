import PropTypes from 'prop-types'
import React from 'react'

const SVGOffers = ({ alt }) => (
  <svg
    height="40px"
    viewBox="0 0 39 40"
    width="39px"
    xmlns="http://www.w3.org/2000/svg"
  >
    {alt && <title>{alt}</title>}
    <g fill="none">
      <g transform="translate(-256.000000, -442.000000)">
        <g transform="translate(255.000000, 437.000000)">
          <rect height="47" width="44" x="0" y="0" />
          <g stroke="#FFFFFF" transform="translate(2.000000, 6.409091)">
            <polygon
              points="15 0 36 0 36 29.9090909 15 29.9090909"
              strokeWidth="2"
            />
            <path
              d="M15,6.32067692 L15,29.9090909 L29.9790759,29.9090909 L13.2312231,34.3966645 L6.33071182,8.64360569 L15,6.32067692 Z"
              strokeWidth="2"
            />
            <path
              d="M7.64863427,13.5917764 L13.2246152,34.4016205 L19.9195166,32.6077271 L11.8437152,37.2702932 L0.541846456,17.6948822 L7.64863427,13.5917764 Z"
              strokeWidth="2"
            />
          </g>
        </g>
      </g>
    </g>
  </svg>
)

SVGOffers.defaultProps = {
  alt: '',
}

SVGOffers.propTypes = {
  alt: PropTypes.string,
}

export { SVGOffers }
