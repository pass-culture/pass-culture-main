/* eslint
  semi: [2, "always"]
  react/jsx-one-expression-per-line: 0 */
import PropTypes from 'prop-types';
import React from 'react';

import { THUMBS_URL, ROOT_PATH } from '../../../utils/config';

const imageSrcBase = `${THUMBS_URL}/mediations`;
const backgroundImage = `url('${ROOT_PATH}/mosaic-k.png')`;

const VersoContentTuto = ({ backgroundColor, mediationId }) => {
  let style = { backgroundImage };
  if (backgroundColor) style = { ...style, backgroundColor };
  return (
    <div className="verso-content" style={style}>
      <img
        alt="verso"
        className="verso-tuto-mediation is-full-width"
        src={`${imageSrcBase}/${mediationId}_1`}
      />
    </div>
  );
};

VersoContentTuto.defaultProps = {
  backgroundColor: null,
};

VersoContentTuto.propTypes = {
  backgroundColor: PropTypes.string,
  mediationId: PropTypes.string.isRequired,
};

export default VersoContentTuto;
