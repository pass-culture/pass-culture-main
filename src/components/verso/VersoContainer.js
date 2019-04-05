/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get';
import { compose } from 'redux';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom';

import Verso from './Verso';
import currentRecommendationSelector from '../../selectors/currentRecommendation';
import { makeDraggable, makeUndraggable } from '../../reducers/card';

export const mapStateToProps = (state, { match }) => {
  const { params } = match;
  const { mediationId, offerId } = params;

  const currentRecommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  );

  const draggable = get(state, 'card.draggable');
  const areDetailsVisible = get(state, 'card.areDetailsVisible');
  return {
    areDetailsVisible,
    currentRecommendation,
    draggable,
  };
};

export const mapDispatchToProps = {
  dispatchMakeDraggable: makeDraggable,
  dispatchMakeUndraggable: makeUndraggable,
};

export default compose(
  withRouter,
  connect(
    mapStateToProps,
    mapDispatchToProps
  )
)(Verso);
