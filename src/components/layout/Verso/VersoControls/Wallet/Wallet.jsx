import React from 'react'
import PropTypes from 'prop-types'

const Wallet = ({ value }) => (
  <div className="verso-wallet">
    <div className="verso-wallet-label">{'Mon pass'}</div>
    <div className="verso-wallet-amount">
      {value}&nbsp;{'€'}
    </div>
  </div>
)

Wallet.propTypes = {
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
}

export default Wallet
