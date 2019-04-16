import PropTypes from 'prop-types'
import React from 'react'
import { Icon } from './Icon'

export const Block = ({
  cancelText,
  confirmText,
  text,
  onConfirmation,
  onCancel,
}) => {
  return (
    <div id="modal-confirm-route-change">
      <ul>
        <li>
          <Icon svg="picto-warning" />
        </li>
        <li>{text}</li>
      </ul>
      <div className="level">
        <button
          className="button is-secondary level-item"
          onClick={onConfirmation}
          type="button">
          {confirmText}
        </button>
        <button
          className="button is-secondary level-item"
          onClick={onCancel}
          type="button">
          {cancelText}
        </button>
      </div>
    </div>
  )
}

Block.defaultProps = {
  cancelText: 'Non',
  confirmText: 'Oui',
  text:
    'Êtes-vous sûr de vouloir quitter cette page ? \
    Les modifications ne seront pas enregistrées.',
}

Block.propTypes = {
  cancelText: PropTypes.string,
  confirmText: PropTypes.string,
  text: PropTypes.string,
  onConfirmation: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
}

export default Block
