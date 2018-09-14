import React from 'react'
import PropTypes from 'prop-types'

const FormFooter = ({
  canCancel,
  canSubmit,
  cancelLabel,
  className,
  submitLabel,
  theme,
}) => (
  <footer
    className={`pc-theme-${theme} pc-footer pc-form-controls flex-end flex-columns flex-0 pl48 ${className}`}
  >
    <button
      type="reset"
      onClick={() => {}}
      disabled={!canCancel}
      className="no-border no-background no-outline no-select fs20 pr20 flex-1"
    >
      <span className="is-full-width is-block text-center">
        {cancelLabel}
      </span>
    </button>
    <button
      type="submit"
      disabled={!canSubmit}
      className="no-border no-background no-outline no-select fs20 pl20 mr12"
    >
      <span className="is-bold">
        {submitLabel}
      </span>
    </button>
  </footer>
)

FormFooter.defaultProps = {
  canCancel: true,
  canSubmit: false,
  cancelLabel: 'Annuler',
  className: '',
  submitLabel: 'Valider',
  theme: 'red',
}

FormFooter.propTypes = {
  canCancel: PropTypes.bool,
  canSubmit: PropTypes.bool,
  cancelLabel: PropTypes.string,
  className: PropTypes.string,
  submitLabel: PropTypes.string,
  theme: PropTypes.string,
}

export default FormFooter
