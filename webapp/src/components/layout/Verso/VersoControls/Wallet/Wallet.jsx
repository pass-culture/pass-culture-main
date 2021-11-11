import PropTypes from 'prop-types'
import React from 'react'

const Wallet = ({ value }) => (
  <div className="verso-wallet">
    <div className="verso-wallet-label">
      {'Mon pass'}
    </div>
    <div className="verso-wallet-amount">
      {`${value} €`}
    </div>
  </div>
)

Wallet.propTypes = {
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
}

export default Wallet
