import React from 'react'
import PropTypes from 'prop-types'

const Wallet = ({ value }) => (
  <div id="verso-wallet">
    <small
      className="is-block"
      id="verso-wallet-label"
    >
      {'Mon pass'}
    </small>
    <span
      className="fs20 is-block"
      id="verso-wallet-value"
    >
      {value}&nbsp;{'€'}
    </span>
  </div>
)

Wallet.propTypes = {
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
}

export default Wallet
