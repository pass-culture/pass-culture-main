/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types';
import React from 'react';

import { THUMBS_URL } from '../../../utils/config';

const imageSrcBase = `${THUMBS_URL}/mediations`;

const VersoContentTuto = ({ mediationId }) => (
  <img
    alt="verso"
    className="verso-tuto-mediation is-full-width"
    src={`${imageSrcBase}/${mediationId}_1`}
  />
);

VersoContentTuto.propTypes = {
  mediationId: PropTypes.string.isRequired,
};

export default VersoContentTuto;
