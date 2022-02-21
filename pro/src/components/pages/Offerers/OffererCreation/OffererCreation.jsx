import createDecorator from 'final-form-calculate'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'
import { Form } from 'react-final-form'
import { removeWhitespaces } from 'react-final-form-utils'
import { NavLink } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import PageTitle from 'components/layout/PageTitle/PageTitle'
import Titles from 'components/layout/Titles/Titles'
import * as pcapi from 'repository/pcapi/pcapi'
import { bindAddressAndDesignationFromSiren } from 'repository/siren/bindSirenFieldToDesignation'

import OffererCreationForm from './OffererCreationForm/OffererCreationForm'
import OffererCreationUnavailable from './OffererCreationUnavailable/OffererCreationUnavailable'

/**
 * @debt standard "Annaëlle: Composant de classe à migrer en fonctionnel"
 */
class OffererCreation extends PureComponent {
  handleSubmit = async offerer => {
    const { siren } = offerer
    await pcapi
      .createOfferer({
        ...offerer,
        siren: removeWhitespaces(siren),
      })
      .then(offerer => {
        this.onHandleSuccess(offerer)
      })
      .catch(() => {
        this.onHandleFail()
      })
  }

  onHandleSuccess = offerer => {
    const { redirectAfterSubmit } = this.props
    const createdOffererId = offerer.id
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
  isEntrepriseApiDisabled: PropTypes.bool.isRequired,
  redirectAfterSubmit: PropTypes.func.isRequired,
  showNotification: PropTypes.func.isRequired,
}

export default OffererCreation
