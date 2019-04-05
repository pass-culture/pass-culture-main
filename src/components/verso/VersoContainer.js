/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get';
import { compose } from 'redux';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom';

import Verso from './Verso';
import currentRecommendationSelector from '../../selectors/currentRecommendation';

export const mapStateToProps = (state, { match }) => {
  const { params } = match;
  const { mediationId, offerId } = params;
  const areDetailsVisible = get(state, 'card.areDetailsVisible');
  const currentRecommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  );
  return {
    areDetailsVisible,
    currentRecommendation,
  };
};

export default compose(
  withRouter,
  connect(mapStateToProps)
)(Verso);
