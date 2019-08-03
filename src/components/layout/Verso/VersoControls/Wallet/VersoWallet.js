import React from 'react'
import PropTypes from 'prop-types'

const VersoWallet = ({ value }) => (
  <div id="verso-wallet">
    <small
      className="is-block"
      id="verso-wallet-label"
    >
      {'Mon pass'}
    </small>
    <span
      className="fs24 is-block"
      id="verso-wallet-value"
    >
      {value}&nbsp;{'€'}
    </span>
  </div>
)

VersoWallet.propTypes = {
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
}

export default VersoWallet
