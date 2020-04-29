import PropTypes from 'prop-types'
import React from 'react'

import { NON_BREAKING_SPACE } from '../../../../utils/specialCharacters'
import { computeEndValidityDate } from '../../../../utils/date/date'

const ProfileHeader = ({ currentUser }) => {
  const {
    publicName,
    wallet_date_created: walletDateCreated,
    wallet_balance: walletBalance,
  } = currentUser
  const endValidityDate = computeEndValidityDate(new Date(walletDateCreated))

  return (
    <section className="ph-wrapper">
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

ProfileHeader.propTypes = {
  currentUser: PropTypes.oneOfType([PropTypes.bool, PropTypes.shape()]).isRequired,
}

export default ProfileHeader
