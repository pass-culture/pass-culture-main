/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import React from 'react';
import PropTypes from 'prop-types';

import Finishable from '../../layout/Finishable';
import { ShareButton } from '../../share/ShareButton';
import VersoWallet from './wallet/VersoWalletContainer';
import VersoButtonFavorite from './favorite/VersoButtonFavoriteContainer';
import VersoBooking from './booking/VersoBooking';
// import VersoBookingButtonContainer from '../verso-buttons/verso-booking-button/VersoBookingButtonContainer';

const renderClickBlockerIfFinished = () => (
  <button
    type="button"
    onClick={() => {}}
    className="finishable-click-blocker"
  />
);

const VersoControl = ({ isFinished }) => (
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
        {isFinished && renderClickBlockerIfFinished()}
        <VersoBooking />
      </li>
    </ul>
    <Finishable finished={isFinished} />
  </div>
);

VersoControl.defaultProps = {
  isFinished: false,
};

VersoControl.propTypes = {
  isFinished: PropTypes.bool,
};

export default VersoControl;
