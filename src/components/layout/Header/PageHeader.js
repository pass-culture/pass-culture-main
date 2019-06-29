import React from 'react'
import PropTypes from 'prop-types'

import BackLink from './BackLink'
import CloseLink from './CloseLink'
import SubmitButton from './SubmitButton'

const PageHeader = ({
  backActionOnClick,
  backTitle,
  backTo,
  closeActionOnClick,
  closeTitle,
  closeTo,
  submitDisabled,
  title,
  useSubmit,
}) => (
  <header className="header">
    {backTo && (
      <div className="header-start">
        <BackLink
          actionOnClick={backActionOnClick}
          backTitle={backTitle}
          backTo={backTo}
        />
      </div>
    )}
    <h1 className="header-title">{title}</h1>
    {closeTo && (
      <div className="header-end">
        <CloseLink
          actionOnClick={closeActionOnClick}
          closeTitle={closeTitle}
          closeTo={closeTo}
        />
      </div>
    )}
    {useSubmit && (
      <div className="header-end">
        <SubmitButton disabled={!submitDisabled} />
      </div>
    )}
  </header>
)

PageHeader.defaultProps = {
  backActionOnClick: null,
  backTitle: 'Retour',
  backTo: null,
  closeActionOnClick: null,
  closeTitle: 'Retourner à la page découverte',
  closeTo: '/decouverte',
  submitDisabled: true,
  useSubmit: false,
}

PageHeader.propTypes = {
  backActionOnClick: PropTypes.func,
  backTitle: PropTypes.string,
  backTo: PropTypes.string,
  closeActionOnClick: PropTypes.func,
  closeTitle: PropTypes.string,
  closeTo: PropTypes.string,
  submitDisabled: PropTypes.bool,
  title: PropTypes.string.isRequired,
  useSubmit: PropTypes.bool,
}

export default PageHeader
