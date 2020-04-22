import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import createDecorator from 'final-form-calculate'

import Main from '../../../layout/Main'
import { bindAddressAndDesignationFromSiren } from './decorators/bindSirenFieldToDesignation'
import OffererCreationForm from './OffererCreationForm/OffererCreationForm'
import Titles from '../../../layout/Titles/Titles'

class OffererCreation extends PureComponent {
  componentWillUnmount() {
    const { closeNotification } = this.props
    closeNotification()
  }

  handleSubmit = values => {
    const { createNewOfferer } = this.props
    createNewOfferer(values, this.onHandleFail, this.onHandleSuccess)
  }

  onHandleSuccess = (_, action) => {
    const { trackCreateOfferer, redirectToOfferersList } = this.props
    const { payload } = action
    const createdOffererId = payload.datum.id

    trackCreateOfferer(createdOffererId)
    redirectToOfferersList()
  }

  onHandleFail = () => {
    const { showNotification } = this.props
    showNotification('Vous étes déjà rattaché à cette structure.', 'danger')
  }

  createDecorators = () => {
    const addressAndDesignationFromSirenDecorator = createDecorator({
      field: 'siren',
      updates: bindAddressAndDesignationFromSiren,
    })

    return [addressAndDesignationFromSirenDecorator]
  }

  render() {
    return (
      <Main
        backTo={{ label: 'Vos structures juridiques', path: '/structures' }}
        name="offerer"
      >
        <Titles title="Structure" />

        <Form
          decorators={this.createDecorators()}
          onSubmit={this.handleSubmit}
          component={OffererCreationForm}
        />
      </Main>
    )
  }
}

OffererCreation.propTypes = {
  closeNotification: PropTypes.func.isRequired,
  createNewOfferer: PropTypes.func.isRequired,
  redirectToOfferersList: PropTypes.func.isRequired,
  showNotification: PropTypes.func.isRequired,
  trackCreateOfferer: PropTypes.func.isRequired,
}

export default OffererCreation
