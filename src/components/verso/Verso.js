/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get';
import classnames from 'classnames';
import PropTypes from 'prop-types';
import React from 'react';

import Footer from '../layout/Footer';
import VersoInfo from './VersoInfo';
import VersoControl from './VersoControl';
import VersoInfoTuto from './VersoInfoTuto';
import { getHeaderColor } from '../../utils/colors';

class Verso extends React.PureComponent {
  componentDidMount() {
    if (!this.$el) return;
    const opts = { passive: true };
    this.$el.addEventListener('touchmove', this.toucheMoveHandler, opts);
  }

  componentDidUpdate(prevProps) {
    const { areDetailsVisible } = this.props;
    const shouldScroll =
      !areDetailsVisible && prevProps.areDetailsVisible && this.$header.scrollTo;
    if (!shouldScroll) return;
    this.$header.scrollTo(0, 0);
  }

  componentWillUnmount() {
    if (!this.$el) return;
    this.$el.removeEventListener('touchmove', this.toucheMoveHandler);
  }

  forwarContainerRefElement = element => {
    this.$el = element;
  }

  forwarHeaderRefElement = element => {
    this.$header = element;
  }

  toucheMoveHandler = () => {
    const {
      draggable,
      dispatchMakeUndraggable,
      dispatchMakeDraggable,
    } = this.props;
    if (draggable && this.$el.scrollTop > 0) {
      dispatchMakeUndraggable();
    } else if (!draggable && this.$el.scrollTop <= 0) {
      dispatchMakeDraggable();
    }
  }

  render() {
    const {
      areDetailsVisible,
      currentRecommendation,
      extraClassName,
      forceDetailsVisible,
    } = this.props;

    const mediation = get(currentRecommendation, 'mediation');
    const tutoIndex = get(currentRecommendation, 'mediation.tutoIndex');
    const offerVenue = get(currentRecommendation, 'offer.venue.name');
    const author = get(
      currentRecommendation,
      'offer.eventOrThing.extraData.author'
    );
    let offerName = get(currentRecommendation, 'offer.eventOrThing.name');
    if (author) offerName = `${offerName}, de ${author}`;

    const isTuto = Boolean(typeof tutoIndex === 'number');

    const flipped = forceDetailsVisible || areDetailsVisible;

    const firstThumbDominantColor = get(
      currentRecommendation,
      'firstThumbDominantColor'
    );
    const backgroundColor = getHeaderColor(firstThumbDominantColor);

    return (
      <div
        className={classnames('verso', extraClassName, {
          flipped,
        })}
      >
        <div
          ref={this.forwarContainerRefElement}
          className="verso-wrapper with-padding-top"
        >
          <div
            className="verso-header"
            style={{ backgroundColor }}
            ref={this.forwarHeaderRefElement}
          >
            <h1
              id="verso-offer-name"
              style={{ lineHeight: '2.7rem' }}
              className="fs40 is-medium is-hyphens"
            >
              {offerName}
            </h1>
            <h2 id="verso-offer-venue" className="fs22 is-normal is-hyphens">
              {offerVenue}
            </h2>
          </div>
          {!isTuto && <VersoControl />}
          {!isTuto && <VersoInfo />}
          {isTuto && <VersoInfoTuto mediationId={mediation.id} />}
        </div>
        <Footer id="verso-footer" borderTop colored={!isTuto} />
      </div>
    );
  }
}

Verso.defaultProps = {
  currentRecommendation: null,
  extraClassName: null,
  forceDetailsVisible: false,
};

Verso.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  currentRecommendation: PropTypes.object,
  dispatchMakeDraggable: PropTypes.func.isRequired,
  dispatchMakeUndraggable: PropTypes.func.isRequired,
  draggable: PropTypes.bool.isRequired,
  extraClassName: PropTypes.string,
  forceDetailsVisible: PropTypes.bool,
};

export default Verso;
