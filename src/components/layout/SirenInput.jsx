import get from 'lodash.get'
import { BasicInput, removeWhitespaces } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { PureComponent, Fragment } from 'react'
import { connect } from 'react-redux'

import { formatSirenOrSiret } from '../../utils/siren'

class SirenInput extends PureComponent {
  handleOnChange = event => {
    const { onChange: onFieldChange, type } = this.props

    event.persist()

    let value = removeWhitespaces(event.target.value)

    if (type === 'siret') {
      value = value.slice(0, Math.min(14, value.length))
    } else if (type === 'siren') {
      value = value.slice(0, Math.min(9, value.length))
    }

    onFieldChange(value, {
      event,
      isSagaCalling: true,
    })
  }

  render() {
    const { errors, fetchedName, readOnly, value, withFetchedName } = this.props

    const $input = (
      <BasicInput
        {...this.props}
        onChange={this.handleOnChange}
        type="text"
        value={formatSirenOrSiret(value)}
      />
    )

    return (
      <Fragment>
        {$input}
        {fetchedName
          ? withFetchedName && <span className="display-name">
            {fetchedName}
                               </span>
          : value && !errors && !readOnly && <button
            className="button is-loading"
            type="button"
                                             />}
      </Fragment>
    )
  }
}

function mapStateToProps(state, ownProps) {
  return {
    fetchedName: get(state, `form.${ownProps.formName}.name`),
  }
}

SirenInput.propTypes = {
  errors: PropTypes.bool.isRequired,
  fetchedName: PropTypes.string.isRequired,
  onFieldChange: PropTypes.func.isRequired,
  readOnly: PropTypes.bool.isRequired,
  type: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  withFetchedName: PropTypes.bool.isRequired,
}

export default connect(mapStateToProps)(SirenInput)
