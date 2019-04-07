/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import React from 'react';
import PropTypes from 'prop-types';

const VersoWallet = ({ value }) => (
  <div id="verso-wallet">
    <small id="verso-wallet-label" className="is-block">
      Mon Pass
    </small>
    <span id="verso-wallet-value" className="fs24 is-block">
      {value}&nbsp;€
    </span>
  </div>
);

VersoWallet.propTypes = {
  value: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
};

export default VersoWallet;
