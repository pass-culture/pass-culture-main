import PropTypes from 'prop-types'
import React from 'react'

export const Block = ({
  cancelText,
  confirmText,
  text,
  onConfirmation,
  onCancel,
}) => {
  return (
    <div>
      <div className="subtitle">{text}</div>
      <div className="level">
        <button
          className="button is-primary level-item"
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
    'Êtes-vous sûr de vouloir quitter cette page ? Les modifications ne seront pas enregistrées.',
}

Block.propTypes = {
  cancelText: PropTypes.string,
  confirmText: PropTypes.string,
  text: PropTypes.string,
  onConfirmation: PropTypes.func.isRequired,
  onCancel: PropTypes.func.isRequired,
}

export default Block
