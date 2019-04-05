/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get';
import PropTypes from 'prop-types';
import React, { Component } from 'react';

import { getHeaderColor } from '../../utils/colors';
import { ROOT_PATH } from '../../utils/config';

const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`;

class VersoWrapper extends Component {
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
    const { children, className, currentRecommendation } = this.props;

    const firstThumbDominantColor = get(
      currentRecommendation,
      'firstThumbDominantColor'
    );
    const backgroundColor = getHeaderColor(firstThumbDominantColor);

    const { mediation, offer } = currentRecommendation || {};
    const { eventOrThing, venue } = offer || {};

    const { tutoIndex } = mediation || {};
    const isTutoView = typeof tutoIndex === 'number';

    const contentStyle = { backgroundImage };
    if (isTutoView) {
      contentStyle.backgroundColor = backgroundColor;
    }

    const offerVenue = get(venue, 'name');
    const author = get(eventOrThing, 'extraData.author');
    let offerName = get(eventOrThing, 'name');
    if (author) offerName = `${offerName}, de ${author}`;
    return (
      <div
        ref={this.forwarContainerRefElement}
        className={`verso-wrapper ${className || ''}`}
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
        {children}
      </div>
    );
  }
}

VersoWrapper.defaultProps = {
  currentRecommendation: null,
};

VersoWrapper.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  children: PropTypes.node.isRequired,
  className: PropTypes.string.isRequired,
  currentRecommendation: PropTypes.object,
  dispatchMakeDraggable: PropTypes.func.isRequired,
  dispatchMakeUndraggable: PropTypes.func.isRequired,
  draggable: PropTypes.bool.isRequired,
};

export default VersoWrapper;
