/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types';
import React from 'react';

const VersoContentTuto = ({ imageURL }) => (
  <img
    alt="verso"
    className="verso-tuto-mediation is-full-width"
    src={imageURL}
  />
);

VersoContentTuto.propTypes = {
  imageURL: PropTypes.string.isRequired,
};

export default VersoContentTuto;
