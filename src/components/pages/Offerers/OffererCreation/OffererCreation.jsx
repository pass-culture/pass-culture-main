import createDecorator from 'final-form-calculate'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'

import AppLayout from 'app/AppLayout'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import { bindAddressAndDesignationFromSiren } from 'repository/siren/bindSirenFieldToDesignation'

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
    redirectAfterSubmit(createdOffererId)
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
    return (
      <AppLayout
        layoutConfig={{
          backTo: { label: 'Accueil', path: '/accueil' },
          pageName: 'offerer',
        }}
      >
        <PageTitle title="Créer une structure" />
        <Titles title="Structure" />

        <Form
          backTo="/accueil"
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
  redirectAfterSubmit: PropTypes.func.isRequired,
  showNotification: PropTypes.func.isRequired,
  trackCreateOfferer: PropTypes.func.isRequired,
}

export default OffererCreation
