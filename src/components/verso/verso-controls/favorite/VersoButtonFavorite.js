/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import React from 'react';
import PropTypes from 'prop-types';
import { Icon } from 'pass-culture-shared';

const DISABLE_FEATURE_NOT_YET_IMPLEMENTED = true;

export const getButtonIcon = isFavorite =>
  isFavorite ? 'ico-like-w-on' : 'ico-like-w';

export const getButtonLabel = isFavorite =>
  isFavorite ? 'Retirer des favoris' : 'Ajouter aux favoris';

const VersoButtonFavorite = ({ isFavorite, onClick, recommendationId }) => (
  <button
    disabled={DISABLE_FEATURE_NOT_YET_IMPLEMENTED}
    onClick={onClick(isFavorite, recommendationId)}
    type="button"
    className="no-border no-background"
  >
    <Icon alt={getButtonLabel(isFavorite)} svg={getButtonIcon(isFavorite)} />
  </button>
);

VersoButtonFavorite.defaultProps = {
  recommendationId: null,
};

VersoButtonFavorite.propTypes = {
  isFavorite: PropTypes.bool.isRequired,
  onClick: PropTypes.func.isRequired,
  recommendationId: PropTypes.string,
};

export default VersoButtonFavorite;
