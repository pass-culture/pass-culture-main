import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import classnames from 'classnames'
import PropTypes from 'prop-types'
import { requestData } from 'redux-saga-data'
import { showNotification } from 'pass-culture-shared'

import Titles from '../../layout/Titles/Titles'
import Main from '../../layout/Main'
import TextField from '../../layout/form/fields/TextField'
import { version } from '../../../../package.json'

class Profil extends PureComponent {
  constructor(props) {
    super(props)

    this.state = {
      isLoading: false,
    }
  }

  handleOnSubmit = formValues => {
    this.setState({ isLoading: true })
    const { dispatch } = this.props
    const { email, publicName } = formValues
    const payload = { email, publicName }

    const config = {
      apiPath: '/users/current',
      body: payload,
      handleSuccess: this.handleSuccess,
      handleFail: this.handleFail,
      method: 'PATCH',
      isMergingDatum: true,
    }
    dispatch(requestData(config))
  }

  handleFail = () => {
    const { dispatch } = this.props
    this.setState({ isLoading: false })

    dispatch(
      showNotification({
        text: 'Erreur lors de la mise à jour de vos informations.',
        type: 'fail',
      })
    )
  }

  handleSuccess = () => {
    const { dispatch } = this.props
    this.setState({ isLoading: false })

    dispatch(
      showNotification({
        text: 'Informations mises à jour avec succès.',
        type: 'success',
      })
    )
  }

  renderForm = ({ handleSubmit }) => {
    const { isLoading } = this.state

    return (
      <form onSubmit={handleSubmit}>
        <div>
          <div className="field-profil-input">
            <TextField
              label="Nom :"
              name="publicName"
              placeholder="3 caractères minimum"
              required
            />
            <TextField
              label="E-mail :"
              name="email"
              required
              type="email"
            />
          </div>

          <div
            className="field is-grouped"
            style={{ justifyContent: 'space-between' }}
          >
            <div className="control">
              <button
                className={classnames('primary-button', {
                  'is-loading': isLoading,
                })}
                type="submit"
              >
                {'Enregistrer'}
              </button>
            </div>
          </div>
        </div>
        <div className="app-version">
          {`v${version}`}
        </div>
      </form>
    )
  }

  render() {
    const { currentUser } = this.props
    const backTo = { path: '/accueil', label: 'Accueil' }

    return (
      <Main
        backTo={backTo}
        name="profile"
      >
        <Titles title="Profil" />
        <Form
          initialValues={currentUser}
          onSubmit={this.handleOnSubmit}
          render={this.renderForm}
        />
        <hr />
      </Main>
    )
  }
}

Profil.propTypes = {
  currentUser: PropTypes.shape({
    email: PropTypes.string,
    publicName: PropTypes.string,
  }).isRequired,
  dispatch: PropTypes.func.isRequired,
}

export default Profil
