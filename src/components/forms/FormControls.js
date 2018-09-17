import React from 'react'
import PropTypes from 'prop-types'

const FormControls = ({
  canCancel,
  canSubmit,
  cancelLabel,
  className,
  isLoading,
  submitLabel,
  theme,
}) => (
  <footer
    className={`pc-theme-${theme} pc-form-controls flex-end flex-columns flex-0 pl48 ${className}`}
  >
    {!isLoading && (
      <React.Fragment>
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
      </React.Fragment>
    )}
    {isLoading && (
      <div className="text-center flex-1">
        <i className="icon-spin6 animate-spin" />
      </div>
    )}
  </footer>
)

FormControls.defaultProps = {
  canCancel: true,
  canSubmit: false,
  cancelLabel: 'Annuler',
  className: '',
  isLoading: false,
  submitLabel: 'Valider',
  theme: 'red',
}

FormControls.propTypes = {
  canCancel: PropTypes.bool,
  canSubmit: PropTypes.bool,
  cancelLabel: PropTypes.string,
  className: PropTypes.string,
  isLoading: PropTypes.bool,
  submitLabel: PropTypes.string,
  theme: PropTypes.string,
}

export default FormControls
