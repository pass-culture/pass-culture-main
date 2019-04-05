/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import classnames from 'classnames';
import PropTypes from 'prop-types';
import React from 'react';

import Footer from '../layout/Footer';
import VersoInfo from './VersoInfo';
import VersoWrapper from './VersoWrapperContainer';

import StaticVerso from './StaticVerso';

class Verso extends React.PureComponent {
  render() {
    const {
      areDetailsVisible,
      currentRecommendation,
      extraClassName,
      forceDetailsVisible,
    } = this.props;
    const { mediation } = currentRecommendation || {};
    const { tutoIndex } = mediation || {};
    const isTuto = typeof tutoIndex === 'number' && mediation;

    const flipped = forceDetailsVisible || areDetailsVisible;
    return (
      <div
        className={classnames('verso', extraClassName, {
          flipped,
        })}
      >
        <VersoWrapper className="with-padding-top">
          {!isTuto && <VersoInfo />}
          {isTuto && <StaticVerso mediationId={mediation.id} />}
        </VersoWrapper>
        <Footer
          id="verso-footer"
          borderTop
          colored={typeof tutoIndex !== 'number'}
        />
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
  extraClassName: PropTypes.string,
  forceDetailsVisible: PropTypes.bool,
};

export default Verso;
