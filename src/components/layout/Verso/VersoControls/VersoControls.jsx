import React from 'react'
import PropTypes from 'prop-types'

import BookThisLinkContainer from './booking/BookThisLink/BookThisLinkContainer'
import CancelThisLinkContainer from './booking/CancelThisLink/CancelThisLinkContainer'
import FavoriteContainer from './Favorite/FavoriteContainer'
import WalletContainer from './Wallet/WalletContainer'
import FinishableContainer from '../../Finishable/FinishableContainer'
import ShareButtonContainer from '../../Share/ShareButton/ShareButtonContainer'

const VersoControls = ({ isBooked }) => (
  <FinishableContainer>
    <ul className="verso-controls">
      <li>
        <WalletContainer />
      </li>
      <li>
        <FavoriteContainer />
      </li>
      <li>
        <ShareButtonContainer />
      </li>
      <li>{isBooked ? <CancelThisLinkContainer /> : <BookThisLinkContainer />}</li>
    </ul>
  </FinishableContainer>
)

VersoControls.defaultProps = {
  isBooked: false,
}

VersoControls.propTypes = {
  isBooked: PropTypes.bool,
}

export default VersoControls
