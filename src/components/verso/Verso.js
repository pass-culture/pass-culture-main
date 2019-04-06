/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import classnames from 'classnames';
import PropTypes from 'prop-types';
import React from 'react';

import Footer from '../layout/Footer';
import VersoInfo from './VersoInfo';
import VersoControl from './VersoControl';
import VersoInfoTuto from './VersoInfoTuto';

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
      backgroundColor,
      extraClassName,
      forceDetailsVisible,
      isTuto,
      mediationId,
      offerName,
      offerVenue,
    } = this.props;

    const flipped = forceDetailsVisible || areDetailsVisible;

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
            {offerName && (
              <h1
                id="verso-offer-name"
                style={{ lineHeight: '2.7rem' }}
                className="fs40 is-medium is-hyphens"
              >
                {offerName}
              </h1>
            )}
            {offerVenue && (
              <h2 id="verso-offer-venue" className="fs22 is-normal is-hyphens">
                {offerVenue}
              </h2>
            )}
          </div>
          {!isTuto && <VersoControl />}
          {!isTuto && <VersoInfo />}
          {isTuto && <VersoInfoTuto mediationId={mediationId} />}
        </div>
        <Footer id="verso-footer" borderTop colored={!isTuto} />
      </div>
    );
  }
}

Verso.defaultProps = {
  backgroundColor: null,
  extraClassName: null,
  forceDetailsVisible: false,
  mediationId: null,
  offerName: null,
  offerVenue: null,
};

Verso.propTypes = {
  areDetailsVisible: PropTypes.bool.isRequired,
  backgroundColor: PropTypes.string,
  dispatchMakeDraggable: PropTypes.func.isRequired,
  dispatchMakeUndraggable: PropTypes.func.isRequired,
  draggable: PropTypes.bool.isRequired,
  extraClassName: PropTypes.string,
  forceDetailsVisible: PropTypes.bool,
  isTuto: PropTypes.bool.isRequired,
  mediationId: PropTypes.string,
  offerName: PropTypes.string,
  offerVenue: PropTypes.string,
};

export default Verso;
