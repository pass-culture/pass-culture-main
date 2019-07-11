import React from 'react'
import PropTypes from 'prop-types'

const VersoPriceFormatter = ({ endingPrice, devise, startingPrice }) => {
  const arrow = '\u27A4'
  return (
    <React.Fragment>
      <span>{startingPrice}</span>
      {endingPrice && (
        <React.Fragment>
          <span className="fs12">
            &nbsp;
            {arrow}
            &nbsp;
          </span>
          <span>{endingPrice}</span>
        </React.Fragment>
      )}
      <span>
        &nbsp;
        {devise}
      </span>
    </React.Fragment>
  )
}

VersoPriceFormatter.defaultProps = {
  endingPrice: null,
}

VersoPriceFormatter.propTypes = {
  devise: PropTypes.string.isRequired,
  endingPrice: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),
  startingPrice: PropTypes.oneOfType([PropTypes.number, PropTypes.string])
    .isRequired,
}

export default VersoPriceFormatter
