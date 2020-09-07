import PropTypes from 'prop-types'
import React from 'react'

import { NON_BREAKING_SPACE } from '../../../../../utils/specialCharacters'
import { computeEndValidityDate } from '../domain/computeEndValidityDate'
import User from '../ValueObjects/User'
import { Link } from 'react-router-dom'
import Icon from '../../../../layout/Icon/Icon'

const Header = ({ user }) => {
  const { publicName, wallet_date_created: walletDateCreated, wallet_balance: walletBalance } = user
  const endValidityDate = computeEndValidityDate(walletDateCreated)

  return (
    <section className="ph-wrapper">
      <Link
        className="ph-back-link"
        to="/accueil"
      >
        <Icon
          svg="ico-arrow-previous"
        />
      </Link>
      <div className="ph-pseudo">
        {`${publicName}`}
      </div>
      <div className="ph-wallet-balance">
        {`${walletBalance}${NON_BREAKING_SPACE}€`}
      </div>
      <div className="ph-end-validity-date">
        {`crédit valable jusqu’au ${endValidityDate}`}
      </div>
    </section>
  )
}

Header.propTypes = {
  user: PropTypes.instanceOf(User).isRequired,
}

export default Header
