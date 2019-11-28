import PropTypes from 'prop-types'
import React from 'react'

import { ROOT_PATH } from '../../utils/config'

const Block = ({ cancelText, confirmText, text, onConfirmation, onCancel }) =>
  (
    <div className="confirm-change">
      <ul>
        <li>
          <img
            alt="picto-warning-orange"
            src={`${ROOT_PATH}/icons/picto-warning-orange.png`}
            title="picto-warning-orange"
          />
        </li>
        <li>
          {text}
        </li>
      </ul>
      <div className="level">
        <button
          className="button is-secondary level-item"
          onClick={onConfirmation}
          type="button"
        >
          {confirmText}
        </button>
        <button
          className="button is-secondary level-item"
          onClick={onCancel}
          type="button"
        >
          {cancelText}
        </button>
      </div>
    </div>
  )

Block.defaultProps = {
  cancelText: 'Non',
  confirmText: 'Oui',
  text: (
    <div className="m12">
      {'Êtes-vous sûr de vouloir quitter cette page ? '}
      <br />
      {'Les modifications ne seront pas enregistrées.'}
    </div>
  ),
}

Block.propTypes = {
  cancelText: PropTypes.string,
  confirmText: PropTypes.string,
  onCancel: PropTypes.func.isRequired,
  onConfirmation: PropTypes.func.isRequired,
  text: PropTypes.string,
}

export default Block
