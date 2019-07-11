/* eslint
  react/jsx-one-expression-per-line: 0 */
import React from 'react'
import PropTypes from 'prop-types'

import Finishable from '../../layout/Finishable'
import { ShareButton } from '../../share/ShareButton'
import VersoWallet from './wallet/VersoWalletContainer'
import VersoButtonFavorite from './favorite/VersoButtonFavoriteContainer'
import CancelThisLinkContainer from './booking/cancel-this-link/CancelThisLinkContainer'
import BookThisLinkContainer from './booking/book-this-link/BookThisLinkContainer'

const VersoControl = ({ booking, isFinished }) => (
  <div className="verso-control is-relative">
    <ul className="py8 px12 is-medium is-flex flex-0 flex-between items-center pc-theme-red">
      <li>
        <VersoWallet />
      </li>
      <li>
        <VersoButtonFavorite />
      </li>
      <li>
        <ShareButton />
      </li>
      <li className="is-relative">
        {booking && (
          <CancelThisLinkContainer
            booking={booking}
            isFinished={isFinished}
          />
        )}
        {!booking && <BookThisLinkContainer isFinished={isFinished} />}
      </li>
    </ul>
    <Finishable finished={isFinished} />
  </div>
)

VersoControl.defaultProps = {
  booking: null,
  isFinished: false,
}

VersoControl.propTypes = {
  booking: PropTypes.object,
  isFinished: PropTypes.bool,
}

export default VersoControl
