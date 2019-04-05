/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import { compose } from 'redux';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom';

import VersoWrapper from './VersoWrapper';
import { makeDraggable, makeUndraggable } from '../../reducers/card';
import currentRecommendationSelector from '../../selectors/currentRecommendation';

export const mapStateToProps = (state, ownProps) => {
  const { mediationId, offerId } = ownProps.match.params;
  const currentRecommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  );
  return {
    areDetailsVisible: state.card.areDetailsVisible,
    currentRecommendation,
    draggable: state.card.draggable,
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
)(VersoWrapper);
