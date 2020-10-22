import React from 'react'
import PropTypes from 'prop-types'
import { blackColor, primaryColor } from 'styles/variables/index.scss'

export const SVGFilter = ({ alt, active }) => (
  <svg
    height="16"
    viewBox="0 0 16 16"
    width="16"
    xmlns="http://www.w3.org/2000/svg"
  >
    <title>
      {alt}
    </title>

    <g
      fill="none"
      fillRule="evenodd"
    >
      <g>
        <g>
          <path
            d="M0 0L16 0 16 16 0 16z"
            transform="translate(-900 -526) translate(900 526)"
          />
          <path
            d="M4.5 12.65c.47 0 .85.38.85.85 0 .433-.324.79-.743.843l-.107.007H1c-.47 0-.85-.38-.85-.85 0-.433.324-.79.743-.843L1 12.65h3.5zm4.5-5c.47 0 .85.38.85.85 0 .433-.324.79-.743.843L9 9.35H1c-.47 0-.85-.38-.85-.85 0-.433.324-.79.743-.843L1 7.65h8zm5.5-5c.47 0 .85.38.85.85 0 .433-.324.79-.743.843l-.107.007H1c-.47 0-.85-.38-.85-.85 0-.433.324-.79.743-.843L1 2.65h13.5z"
            fill={active ? primaryColor : blackColor}
            transform="translate(-900 -526) translate(900 526)"
          />
        </g>
      </g>
    </g>
  </svg>
)
SVGFilter.defaultProps = {
  active: false,
  alt: '',
}

SVGFilter.propTypes = {
  active: PropTypes.bool,
  alt: PropTypes.string,
}
