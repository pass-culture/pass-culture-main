import React from 'react'
import PropTypes from 'prop-types'

import BookThisLinkContainer from './booking/BookThisLink/BookThisLinkContainer'
import CancelThisLinkContainer from './booking/CancelThisLink/CancelThisLinkContainer'
import FavoriteContainer from './Favorite/FavoriteContainer'
import WalletContainer from './Wallet/WalletContainer'
import FinishableContainer from '../../Finishable/FinishableContainer'
import ShareButtonContainer from '../../Share/ShareButton/ShareButtonContainer'

const VersoControls = ({ showCancelView }) => {
  return (
    <div className="verso-controls is-relative">
      <ul className="py8 px12 is-medium is-flex flex-0 flex-between items-center pc-theme-red">
        <li>
          <WalletContainer />
        </li>
        <li>
          <FavoriteContainer />
        </li>
        <li>
          <ShareButtonContainer />
        </li>
        <li className="is-relative">
          {showCancelView ? <CancelThisLinkContainer /> : <BookThisLinkContainer />}
        </li>
      </ul>
      <FinishableContainer />
    </div>
  )
}

VersoControls.defaultProps = {
  showCancelView: null,
}

VersoControls.propTypes = {
  showCancelView: PropTypes.bool,
}

export default VersoControls
