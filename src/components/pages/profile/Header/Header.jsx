import PropTypes from 'prop-types'
import React from 'react'

import { formatDate } from '../../../../utils/date/date'
import { NON_BREAKING_SPACE } from '../../../../utils/specialCharacters'
import User from '../ValueObjects/User'

const Header = ({ user }) => {
  const {
    publicName,
    deposit_expiration_date: depositExpirationDateIso,
    wallet_balance: walletBalance,
  } = user

  const formattedExpirationDate = formatDate(new Date(depositExpirationDateIso))

  return (
    <section className="ph-wrapper">
      <div className="ph-pseudo">
        {`${publicName}`}
      </div>
      <div className="ph-wallet-balance">
        {`${walletBalance}${NON_BREAKING_SPACE}€`}
      </div>
      {user.isBeneficiary && (
        <div className="ph-end-validity-date">
          {`crédit valable jusqu’au ${formattedExpirationDate}`}
        </div>
      )}
    </section>
  )
}

Header.propTypes = {
  user: PropTypes.shape(User).isRequired,
}

export default Header
