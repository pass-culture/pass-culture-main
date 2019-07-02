import React from 'react'
import PropTypes from 'prop-types'
import { Field } from 'react-final-form'
import { HiddenField, TextField } from '../../../../../layout/form/fields'
import Icon from '../../../../../layout/Icon'
import SelectSourceField from '../SelectSourceField/SelectSourceField'
import classNames from 'classnames'

const VenueProviderForm = ({
  handleChange,
  isProviderSelected,
  isLoadingMode,
  isCreationMode,
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
              <Icon svg="picto-db-default" alt="Choix de la source" />
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
              'field-is-read-only':
                !venueIdAtOfferProviderIsRequired || isLoadingMode,
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
              data-tip={`<p>Veuillez saisir un compte.</p>`}>
              <Icon svg="picto-info" alt="image d'aide à l'information" />
            </span>
          )}
        </div>
      )}

      {isProviderSelected && isCreationMode && !isLoadingMode && (
        <div className="provider-import-button-container">
          <button
            className="button is-intermediate provider-import-button"
            type="submit">
            Importer
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
  providers: PropTypes.array.isRequired,
  venueProviders: PropTypes.array.isRequired,
  venueIdAtOfferProviderIsRequired: PropTypes.bool.isRequired,
}

export default VenueProviderForm
