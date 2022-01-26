/*
 * @debt directory "Gaël: this file should be migrated within the new directory structure"
 * @debt deprecated "Gaël: deprecated usage of react-final-form"
 * @debt standard "Gaël: migration from classes components to function components"
 */

import createDecorator from 'final-form-calculate'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import { NavLink } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import { bindAddressAndDesignationFromSiren } from 'repository/siren/bindSirenFieldToDesignation'

import OffererCreationForm from './OffererCreationForm/OffererCreationForm'
import OffererCreationUnavailable from './OffererCreationUnavailable/OffererCreationUnavailable'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
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
    const { isEntrepriseApiDisabled } = this.props
    return (
      <div className="offerer-page">
        <NavLink className="back-button has-text-primary" to="/accueil">
          <Icon svg="ico-back" />
          Accueil
        </NavLink>
        <PageTitle title="Créer une structure" />
        <Titles title="Structure" />
        {isEntrepriseApiDisabled ? (
          <OffererCreationUnavailable />
        ) : (
          <Form
            backTo="/accueil"
            component={OffererCreationForm}
            decorators={this.createDecorators()}
            onSubmit={this.handleSubmit}
          />
        )}
      </div>
    )
  }
}

OffererCreation.propTypes = {
  createNewOfferer: PropTypes.func.isRequired,
  isEntrepriseApiDisabled: PropTypes.bool.isRequired,
  redirectAfterSubmit: PropTypes.func.isRequired,
  showNotification: PropTypes.func.isRequired,
  trackCreateOfferer: PropTypes.func.isRequired,
}

export default OffererCreation
