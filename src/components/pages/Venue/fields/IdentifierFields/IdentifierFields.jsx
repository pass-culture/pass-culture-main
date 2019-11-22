import PropTypes from 'prop-types'
import React, { Fragment, PureComponent } from 'react'

import siretValidate from './validators/siretValidate'
import Icon from '../../../../layout/Icon'
import HiddenField from '../../../../layout/form/fields/HiddenField'
import TextareaField from '../../../../layout/form/fields/TextareaField'
import TextField from '../../../../layout/form/fields/TextField'
import { formatSiret } from '../../siret/formatSiret'
import ReactTooltip from 'react-tooltip'


class IdentifierFields extends PureComponent {
  componentDidUpdate() {
    ReactTooltip.rebuild()
  }

  handleRenderValue = (fieldReadOnlyBecauseFrozenFormSiret, readOnly) => () => {
    if (readOnly) {
      return null
    }
    if (fieldReadOnlyBecauseFrozenFormSiret) {
      return (
        <span
          className="button"
          data-place="bottom"
          data-tip="<p>Il n’est pas possible de modifier le nom, l’addresse et la géolocalisation du lieu quand un siret est renseigné.</p>"
          data-type="info"
        >
          <Icon svg="picto-info" />
        </span>
      )
    }
    return (
      <span
        className="button"
        data-place="bottom"
        data-tip="<div><p>Saisissez ici le SIRET du lieu lié à votre structure pour retrouver ses informations automatiquement.</p>
        <p>Si les informations ne correspondent pas au SIRET saisi, <a href='mailto:pass@culture.gouv.fr?subject=Question%20SIRET'> contactez notre équipe</a>.</p></div>"
        data-type="info"
      >
        <Icon svg="picto-info" />
      </span>
    )
  }

  handleRender = readOnly => () => {
    if (readOnly) {
      return null
    }
    return (
      <span
        className="button"
        data-place="bottom"
        data-tip="<p>Cette adresse recevra les e-mails de notification de réservation (sauf si une adresse différente est saisie lors de la création d’une offre)</p>"
        data-type="info"
      >
        <Icon svg="picto-info" />
      </span>
    )
  }

  commentValidate = comment => {
    const {
      formSiret,
    } = this.props

    if (formSiret && formSiret.length === 14) {
      return ''
    }
    if (comment === undefined || comment === '') {
      return 'Ce champ est obligatoire'
    }
    return ''
  }

  render() {
    const {
      fieldReadOnlyBecauseFrozenFormSiret,
      initialSiret,
      isCreatedEntity,
      readOnly,
    } = this.props

    return (
      <div className="section">
        <h2 className="main-list-title is-relative">
          {'INFORMATIONS DU LIEU'}
          {!readOnly && (
            <span className="is-pulled-right fs13 has-text-grey">
              {'Les champs marqués d’un'}
              <span className="required-legend">
                {' * '}
              </span>
              {' sont obligatoires'}
            </span>
          )}
        </h2>
        <div className="field-group">
          {isCreatedEntity && <HiddenField name="managingOffererId" />}
          <div className="field text-field is-label-aligned">
            <label
              className="field-label"
              htmlFor="siret"
            >
              {isCreatedEntity ? (
                <Fragment>
                  {'SIRET'}
                  <span className="siret-label-details">
                    <span className="siret-label-bold">
                      {' du lieu qui accueille vos offres'}
                    </span>
                    {' (si applicable) : '}
                  </span>
                </Fragment>
              ) : (
                'SIRET : '
              )}
            </label>
            <TextField
              format={formatSiret}
              name="siret"
              readOnly={readOnly || initialSiret !== null}
              renderValue={this.handleRenderValue(fieldReadOnlyBecauseFrozenFormSiret, readOnly)}
              type="siret"
              {...(initialSiret ? {} : { validate: siretValidate })}
            />
          </div>
          <TextField
            label="Nom du lieu : "
            name="name"
            readOnly={readOnly || fieldReadOnlyBecauseFrozenFormSiret}
            required
          />
          <TextField
            label="Nom d’usage du lieu : "
            name="publicName"
            readOnly={readOnly}
          />
          <TextField
            innerClassName="col-75"
            label="E-mail : "
            name="bookingEmail"
            readOnly={readOnly}
            renderValue={this.handleRender(readOnly)}
            required
            type="email"
          />
          <TextareaField
            label="Commentaire (si pas de SIRET) : "
            name="comment"
            readOnly={readOnly}
            rows={1}
            validate={this.commentValidate}
          />
        </div>
      </div>
    )
  }
}

IdentifierFields.defaultProps = {
  fieldReadOnlyBecauseFrozenFormSiret: false,
  formSiret: null,
  initialSiret: null,
  readOnly: true,
}

IdentifierFields.propTypes = {
  fieldReadOnlyBecauseFrozenFormSiret: PropTypes.bool,
  formSiret: PropTypes.string,
  initialSiret: PropTypes.string,
  isCreatedEntity: PropTypes.bool.isRequired,
  readOnly: PropTypes.bool,
}

export default IdentifierFields
