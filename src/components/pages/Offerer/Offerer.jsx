import classnames from 'classnames'
import { Field, Form } from 'pass-culture-shared'
import PropTypes from 'prop-types'
import React, { PureComponent } from 'react'

import { OffererClass } from './OffererClass'
import CreationControl from './CreationControl/CreationControl'
import ModificationControl from './ModificationControl/ModificationControl'
import Venues from './Venues/Venues'
import HeroSection from '../../layout/HeroSection/HeroSection'
import Main from '../../layout/Main'
import { formatPatch } from '../../../utils/formatPatch'

const OFFERER_CREATION_PATCH_KEYS = ['address', 'city', 'name', 'siren', 'postalCode']
const OFFERER_MODIFICATION_PATCH_KEYS = ['bic', 'iban', 'rib']

class Offerer extends PureComponent {
  onHandleDataRequest = (handleSuccess, handleFail) => {
    const { getOfferer, getUserOfferers, query } = this.props
    const { isCreatedEntity } = query.context()

    if (!isCreatedEntity) {
      getOfferer(handleFail, handleSuccess)
      getUserOfferers()
      return
    }
    handleSuccess()
  }

  onHandleFail = () => {
    const { showNotification } = this.props
    showNotification('Vous étes déjà rattaché à cette structure.', 'danger')
  }

  onHandleSuccess = (state, action) => {
    const { payload } = action
    const createdOffererId = payload.datum.id
    const {
      offerer,
      history,
      query,
      showNotification,
      trackCreateOfferer,
      trackModifyOfferer,
    } = this.props
    const { isCreatedEntity } = query.context()

    if (isCreatedEntity) {
      trackCreateOfferer(createdOffererId)
    } else {
      trackModifyOfferer(offerer.id)
    }

    history.push('/structures')

    const text = isCreatedEntity
      ? 'Votre structure a bien été enregistrée, elle est en cours de validation.'
      : 'Les modifications sur votre structure ont bien été prises en compte.'

    showNotification(text, 'success')
  }

  handleDisabling = offererName => () => !offererName

  formatPatch = patchConfig => patch =>
    formatPatch(patch, patchConfig, OFFERER_CREATION_PATCH_KEYS, OFFERER_MODIFICATION_PATCH_KEYS)

  render() {
    const { offerer, query, venues, formCurrentValues } = this.props
    const { offererName } = formCurrentValues
    const { isCreatedEntity, isModifiedEntity, readOnly } = query.context()
    const areBankInfosReadOnly = readOnly || !offerer.adminUserOfferer

    const patchConfig = { isCreatedEntity, isModifiedEntity }

    return (
      <Main
        backTo={{ label: 'Vos structures juridiques', path: '/structures' }}
        handleDataRequest={this.onHandleDataRequest}
        name="offerer"
      >
        <HeroSection
          subtitle={offerer.name}
          title="Structure"
        >
          <p className="subtitle">
            {'Détails de la structure rattachée, des lieux et des fournisseurs de ses offres.'}
          </p>
        </HeroSection>

        <Form
          action={`/offerers/${offerer.id || ''}`}
          className="section"
          formatPatch={this.formatPatch(patchConfig)}
          handleFail={this.onHandleFail}
          handleSuccess={this.onHandleSuccess}
          name="offerer"
          patch={offerer}
          readOnly={readOnly}
        >
          <div className="section">
            <div className="field-group">
              <Field
                disabling={this.handleDisabling(offererName)}
                label="SIREN"
                name="siren"
                readOnly={offerer.id}
                required
                type="siren"
              />
              <Field
                className={classnames({
                  'is-invisible': !offerer.isIdOrNameDefined,
                })}
                isExpanded
                label="Désignation"
                name="name"
                readOnly
                required
              />
              <Field
                className={classnames({
                  'is-invisible': !offerer.isIdOrNameDefined,
                })}
                isExpanded
                label="Siège social"
                name="address"
                readOnly
              />
            </div>
          </div>
          <div className="section">
            <h2 className="main-list-title">
              {'Informations bancaires'}
              <span className="is-pulled-right is-size-7 has-text-grey">
                {readOnly &&
                  !offerer.adminUserOfferer &&
                  "Vous avez besoin d'être administrateur de la structure pour modifier ces informations."}
              </span>
            </h2>
            {offerer.name && !offerer.areBankInformationProvided() && (
              <p className="bank-instructions-label">
                {
                  'Le pass Culture vous contactera prochainement afin d’enregistrer vos coordonnées bancaires. Une fois votre BIC / IBAN renseigné, ces informations apparaitront ci-dessous.'
                }
              </p>
            )}
            <div className="field-group">
              <Field
                className={classnames({
                  'is-invisible': !offerer.isIdOrNameDefined,
                })}
                isExpanded
                label="BIC"
                name="bic"
                readOnly={areBankInfosReadOnly}
                type="bic"
              />
              <Field
                className={classnames({
                  'is-invisible': !offerer.isIdOrNameDefined,
                })}
                isExpanded
                label="IBAN"
                name="iban"
                readOnly={areBankInfosReadOnly}
                type="iban"
              />
            </div>
            {isCreatedEntity ? <CreationControl /> : <ModificationControl {...this.props} />}
            <div>
              {!isCreatedEntity && <Venues
                offererId={offerer.id}
                venues={venues}
                                   />}
            </div>
          </div>
        </Form>
      </Main>
    )
  }
}

Offerer.propTypes = {
  formCurrentValues: PropTypes.shape().isRequired,
  getOfferer: PropTypes.func.isRequired,
  getUserOfferers: PropTypes.func.isRequired,
  history: PropTypes.shape().isRequired,
  offerer: PropTypes.instanceOf(OffererClass).isRequired,
  query: PropTypes.shape().isRequired,
  showNotification: PropTypes.func.isRequired,
  trackCreateOfferer: PropTypes.func.isRequired,
  trackModifyOfferer: PropTypes.func.isRequired,
}

export default Offerer
