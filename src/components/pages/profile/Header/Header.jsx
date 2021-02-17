import PropTypes from 'prop-types'
import React from 'react'

import { LOCALE_FRANCE, MONTH_IN_NUMBER, YEAR_IN_NUMBER } from '../../../../utils/date/date'
import { NON_BREAKING_SPACE } from '../../../../utils/specialCharacters'
import User from '../ValueObjects/User'

const Header = ({ user }) => {
  const {
    publicName,
    deposit_expiration_date: depositExpirationDateIso,
    wallet_balance: walletBalance,
  } = user

  const formattedExpirationDate = new Date(depositExpirationDateIso).toLocaleDateString(
    LOCALE_FRANCE,
    {
      ...YEAR_IN_NUMBER,
      ...MONTH_IN_NUMBER,
      day: 'numeric',
    }
  )

  return (
    <section className="ph-wrapper">
      <div className="ph-pseudo">
        {`${publicName}`}
      </div>
      <div className="ph-wallet-balance">
        {`${walletBalance}${NON_BREAKING_SPACE}€`}
      </div>
      <div className="ph-end-validity-date">
        {`crédit valable jusqu’au ${formattedExpirationDate}`}
      </div>
    </section>
  )
}

Header.propTypes = {
  user: PropTypes.shape(User).isRequired,
}

export default Header
