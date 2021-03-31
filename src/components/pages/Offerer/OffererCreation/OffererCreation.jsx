import createDecorator from 'final-form-calculate'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'

import AppLayout from 'app/AppLayout'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'

import { bindAddressAndDesignationFromSiren } from './decorators/bindSirenFieldToDesignation'
import OffererCreationForm from './OffererCreationForm/OffererCreationForm'

class OffererCreation extends PureComponent {
  handleSubmit = values => {
    const { createNewOfferer } = this.props
    createNewOfferer(values, this.onHandleFail, this.onHandleSuccess)
  }

  onHandleSuccess = (_, action) => {
    const { trackCreateOfferer, redirectAfterSubmit } = this.props
    const { payload } = action
    const createdOffererId = payload.datum.id

    trackCreateOfferer(createdOffererId)
    redirectAfterSubmit()
  }

  onHandleFail = () => {
    const { showNotification } = this.props
    showNotification('Vous étes déjà rattaché à cette structure.', 'error')
  }

  createDecorators = () => {
    const addressAndDesignationFromSirenDecorator = createDecorator({
      field: 'siren',
      updates: bindAddressAndDesignationFromSiren,
    })

    return [addressAndDesignationFromSirenDecorator]
  }

  render() {
    const { isNewHomepageActive } = this.props
    return (
      <AppLayout
        layoutConfig={{
          backTo: isNewHomepageActive
            ? { label: 'Accueil', path: '/accueil' }
            : { label: 'Structures juridiques', path: '/structures' },
          pageName: 'offerer',
        }}
      >
        <PageTitle title="Créer une structure" />
        <Titles title="Structure" />

        <Form
          backTo={isNewHomepageActive ? '/accueil' : '/structures'}
          component={OffererCreationForm}
          decorators={this.createDecorators()}
          onSubmit={this.handleSubmit}
        />
      </AppLayout>
    )
  }
}

OffererCreation.propTypes = {
  createNewOfferer: PropTypes.func.isRequired,
  isNewHomepageActive: PropTypes.bool.isRequired,
  redirectAfterSubmit: PropTypes.func.isRequired,
  showNotification: PropTypes.func.isRequired,
  trackCreateOfferer: PropTypes.func.isRequired,
}

export default OffererCreation
