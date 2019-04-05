/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types';
import React from 'react';

import { THUMBS_URL } from '../../utils/config';

const VersoInfoTuto = ({ mediationId }) => (
  <img
    alt="verso"
    className="verso-tuto-mediation"
    src={`${THUMBS_URL}/mediations/${mediationId}_1`}
  />
);

VersoInfoTuto.propTypes = {
  mediationId: PropTypes.string.isRequired,
};

export default VersoInfoTuto;
