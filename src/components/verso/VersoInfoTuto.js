/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types';
import React from 'react';

import { THUMBS_URL, ROOT_PATH } from '../../utils/config';

const imageSrcBase = `${THUMBS_URL}/mediations`;
const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`;

const VersoInfoTuto = React.memo(({ backgroundColor, mediationId }) => (
  <div
    className="verso-content"
    style={{
      backgroundColor,
      backgroundImage,
    }}
  >
    <img
      alt="verso"
      className="verso-tuto-mediation"
      src={`${imageSrcBase}/${mediationId}_1`}
    />
  </div>
));

VersoInfoTuto.propTypes = {
  backgroundColor: PropTypes.string.isRequired,
  mediationId: PropTypes.string.isRequired,
};

export default VersoInfoTuto;
