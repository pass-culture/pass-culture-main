import React, { Fragment } from 'react'
import PropTypes from 'prop-types'

const VersoPriceFormatter = ({ endingPrice, devise, startingPrice }) => {
  const arrow = '\u27A4'
  return (
    <Fragment>
      <span>{startingPrice}</span>
      {endingPrice && (
        <Fragment>
          <span className="fs12">
            &nbsp;
            {arrow}
            &nbsp;
          </span>
          <span>{endingPrice}</span>
        </Fragment>
      )}
      <span>
        &nbsp;
        {devise}
      </span>
    </Fragment>
  )
}

VersoPriceFormatter.defaultProps = {
  endingPrice: null,
}

VersoPriceFormatter.propTypes = {
  devise: PropTypes.string.isRequired,
  endingPrice: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  startingPrice: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
}

export default VersoPriceFormatter
