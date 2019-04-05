/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import get from 'lodash.get';
import classnames from 'classnames';
import PropTypes from 'prop-types';
import React from 'react';

import Footer from '../layout/Footer';
import VersoInfo from './VersoInfo';
import VersoWrapper from './VersoWrapper';
import VersoControl from './VersoControl';
import StaticVerso from './StaticVerso';
import { getHeaderColor } from '../../utils/colors';
import { ROOT_PATH } from '../../utils/config';

const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`;

class Verso extends React.PureComponent {
  render() {
    const {
      areDetailsVisible,
      currentRecommendation,
      dispatchMakeDraggable,
      dispatchMakeUndraggable,
      draggable,
      extraClassName,
      forceDetailsVisible,
    } = this.props;
    const mediation = get(currentRecommendation, 'mediation');
    const tutoIndex = get(mediation, 'tutoIndex');
    const isTuto = Boolean(typeof tutoIndex === 'number');

    const flipped = forceDetailsVisible || areDetailsVisible;

    const firstThumbDominantColor = get(
      currentRecommendation,
      'firstThumbDominantColor'
    );
    const backgroundColor = getHeaderColor(firstThumbDominantColor);

    const contentStyle = { backgroundImage };
    if (isTuto) {
      contentStyle.backgroundColor = backgroundColor;
    }

    return (
      <div
        className={classnames('verso', extraClassName, {
          flipped,
        })}
      >
        <VersoWrapper
          className="with-padding-top"
          areDetailsVisible={areDetailsVisible}
          currentRecommendation={currentRecommendation}
          dispatchMakeDraggable={dispatchMakeDraggable}
          dispatchMakeUndraggable={dispatchMakeUndraggable}
          draggable={draggable}
        >
          {!isTuto && <VersoControl />}
          <div className="verso-content" style={{ ...contentStyle }}>
            {!isTuto && <VersoInfo />}
            {isTuto && <StaticVerso mediationId={mediation.id} />}
          </div>
        </VersoWrapper>
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
