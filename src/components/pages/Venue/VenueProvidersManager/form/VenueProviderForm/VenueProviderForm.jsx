import classNames from 'classnames'
import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'

import HiddenField from '../../../../../layout/form/fields/HiddenField'
import TextField from '../../../../../layout/form/fields/TextField'
import NumberField from '../../../../../layout/form/fields/NumberField'
import Icon from '../../../../../layout/Icon'
import SelectSourceField from '../SelectSourceField/SelectSourceField'

const VenueProviderForm = ({
  handleChange,
  isProviderSelected,
  isLoadingMode,
  isCreationMode,
  providerSelectedIsAllocine,
  providers,
  venueProviders,
  venueIdAtOfferProviderIsRequired,
}) => ({ handleSubmit }) => (
  <form onSubmit={handleSubmit}>
    <div className="venue-provider-table">
      <HiddenField name="id" />
      <div className="provider-container">
        <div className="provider-picto">
          <span className="field picto">
            <label htmlFor="provider-options">
              <Icon
                alt="Choix de la source"
                svg="picto-db-default"
              />
            </label>
          </span>
        </div>

        <Field
          name="provider"
          render={SelectSourceField({
            handleChange,
            providers,
            venueProviders,
          })}
          required
        />
      </div>

      {isProviderSelected && (
        <div className="venue-id-at-offer-provider-container">
          <TextField
            className={classNames('field-text fs12', {
              'field-is-read-only': !venueIdAtOfferProviderIsRequired || isLoadingMode,
            })}
            label="Compte : "
            name="venueIdAtOfferProvider"
            readOnly={!venueIdAtOfferProviderIsRequired || isLoadingMode}
            required
          />

          {!isLoadingMode && venueIdAtOfferProviderIsRequired && (
            <span
              className="tooltip tooltip-info"
              data-place="bottom"
              data-tip={`<p>Veuillez saisir un compte.</p>`}
            >
              <Icon
                alt="image d’aide à l’information"
                svg="picto-info"
              />
            </span>
          )}

          {!isLoadingMode && providerSelectedIsAllocine && (
            <div className="price-container">
              <NumberField
                className={classNames('field-text fs12')}
                label="Prix de vente/place: "
                name="price"
                placeholder="Ex : 12€"
                required
              />
              <span
                className="tooltip tooltip-info"
                data-place="bottom"
                data-tip={`<p>Prix de vente/place : Prix auquel la place de cinéma sera vendue</p>`}
              >
                <Icon
                  alt="image d’aide à l’information"
                  svg="picto-info"
                />
              </span>
            </div>
          )}
        </div>
      )}

      {isProviderSelected && isCreationMode && !isLoadingMode && (
        <div className="provider-import-button-container">
          <button
            className="button is-intermediate provider-import-button"
            type="submit"
          >
            {'Importer'}
          </button>
        </div>
      )}
    </div>
  </form>
)

VenueProviderForm.propTypes = {
  handleChange: PropTypes.func.isRequired,
  isCreationMode: PropTypes.bool.isRequired,
  isLoadingMode: PropTypes.bool.isRequired,
  isProviderSelected: PropTypes.bool.isRequired,
  providerSelectedIsAllocine: PropTypes.bool.isRequired,
  providers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  venueIdAtOfferProviderIsRequired: PropTypes.bool.isRequired,
  venueProviders: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default VenueProviderForm
