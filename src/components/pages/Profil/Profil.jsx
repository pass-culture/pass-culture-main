import React from 'react'
import HeroSection from '../../layout/HeroSection'
import Main from '../../layout/Main'
import { Form } from 'react-final-form'
import PropTypes from 'prop-types'
import { TextField } from '../../layout/form/fields'
import { requestData } from 'redux-saga-data'
import classnames from 'classnames'
import { showNotification } from 'pass-culture-shared'

class Profil extends React.Component {
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

  render() {
    const { currentUser } = this.props
    const { isLoading } = this.state
    const backTo = { path: '/accueil', label: 'Accueil' }

    return (
      <Main name="profile" backTo={backTo}>
        <HeroSection title="Profil" />
        <Form
          onSubmit={this.handleOnSubmit}
          initialValues={currentUser}
          render={({ handleSubmit }) => (
            <form onSubmit={handleSubmit}>
              <div>
                <div className="field-profil-input">
                  <TextField
                    name="publicName"
                    label="Nom :"
                    placeholder="3 caractères minimum"
                    required
                  />
                  <TextField name="email" type="email" label="E-mail :" required />
                </div>

                <div
                  className="field is-grouped"
                  style={{ justifyContent: 'space-between' }}>
                  <div className="control">
                    <button
                      className={classnames('button is-primary is-medium', {
                        'is-loading': isLoading,
                      })}
                      type="submit">
                      Enregistrer
                    </button>
                  </div>
                </div>
              </div>
            </form>
          )}
        />
        <hr />
      </Main>
    )
  }
}

PropTypes.propTypes = {
  currentUser: PropTypes.shape({
    email: PropTypes.string,
    publicName: PropTypes.string,
  }).isRequired,
  dispatch: PropTypes.func.isRequired,
}

export default Profil
