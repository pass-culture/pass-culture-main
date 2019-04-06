/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get';
import { compose } from 'redux';
import { connect } from 'react-redux';
import { withRouter } from 'react-router-dom';

import Verso from './Verso';
import { getHeaderColor } from '../../utils/colors';
import currentRecommendationSelector from '../../selectors/currentRecommendation';
import { makeDraggable, makeUndraggable } from '../../reducers/card';

export const checkIsTuto = recommendation => {
  const tutoIndex = get(recommendation, 'mediation.tutoIndex');
  const result = Boolean(typeof tutoIndex === 'number');
  return result;
};

export const getOfferVenue = recommendation => {
  const result = get(recommendation, 'offer.venue.name');
  return result;
};

export const getOfferName = recommendation => {
  const author = get(recommendation, 'offer.eventOrThing.extraData.author');
  let result = get(recommendation, 'offer.eventOrThing.name');
  if (author) result = `${result}, de ${author}`;
  return result;
};

export const getBackgroundColor = recommendation => {
  const firstThumbDominantColor = get(recommendation, 'firstThumbDominantColor');
  const result = getHeaderColor(firstThumbDominantColor);
  return result;
};

export const mapStateToProps = (state, { match }) => {
  const { params } = match;
  const { mediationId, offerId } = params;

  const recommendation = currentRecommendationSelector(
    state,
    offerId,
    mediationId
  );

  const backgroundColor = getBackgroundColor(recommendation);
  const isTuto = checkIsTuto(recommendation);
  const offerVenue = getOfferVenue(recommendation);
  const offerName = getOfferName(recommendation);

  const draggable = get(state, 'card.draggable');
  const areDetailsVisible = get(state, 'card.areDetailsVisible');

  return {
    areDetailsVisible,
    backgroundColor,
    draggable,
    isTuto,
    mediationId,
    offerName,
    offerVenue,
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
