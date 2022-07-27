import PropTypes from 'prop-types'
import React from 'react'

import HiddenField from 'components/layout/form/fields/HiddenField'
import NumberField from 'components/layout/form/fields/NumberField'
import TextField from 'components/layout/form/fields/TextField'
import {
  parsePostalCode,
  validatePostalCode,
} from 'components/layout/form/validate'

import AddressField from './AddressField'

const COORDINATE_ACCURACY = 0.000001

const LocationFields = ({
  fieldReadOnlyBecauseFrozenFormSiret,
  form,
  formLatitude,
  formLongitude,
  formIsLocationFrozen,
  readOnly,
  isAddressRequired,
}) => {
  const fieldIsFrozen =
    readOnly || formIsLocationFrozen || fieldReadOnlyBecauseFrozenFormSiret
  return (
    <div className="section">
      <h2 className="main-list-title">Adresse</h2>
      <div className="field-group">
        <HiddenField name="isLocationFrozen" />
        <AddressField
          className="vp-field"
          form={form}
          id="address"
          label="Numéro et voie : "
          latitude={formLatitude}
          longitude={formLongitude}
          name="address"
          readOnly={readOnly || fieldReadOnlyBecauseFrozenFormSiret}
          withMap
          required={isAddressRequired}
        />
        <TextField
          autoComplete="postal-code"
          className="vp-field"
          innerClassName="col-33"
          label="Code postal : "
          name="postalCode"
          parse={parsePostalCode}
          readOnly={fieldIsFrozen}
          required
          validate={validatePostalCode}
        />
        <TextField
          autoComplete="address-level2"
          className="vp-field"
          innerClassName="col-66"
          label="Ville : "
          name="city"
          readOnly={fieldIsFrozen}
          required
        />
        <NumberField
          className="vp-field"
          innerClassName="col-33"
          label="Latitude : "
          name="latitude"
          readOnly={fieldIsFrozen}
          required
          step={COORDINATE_ACCURACY}
        />
        <NumberField
          className="vp-field"
          innerClassName="col-33"
          label="Longitude : "
          name="longitude"
          readOnly={fieldIsFrozen}
          required
          step={COORDINATE_ACCURACY}
        />
      </div>
    </div>
  )
}

LocationFields.defaultProps = {
  fieldReadOnlyBecauseFrozenFormSiret: false,
  formIsLocationFrozen: false,
  formLatitude: null,
  formLongitude: null,
  readOnly: true,
}

LocationFields.propTypes = {
  fieldReadOnlyBecauseFrozenFormSiret: PropTypes.bool,
  form: PropTypes.shape().isRequired,
  formIsLocationFrozen: PropTypes.bool,
  formLatitude: PropTypes.number,
  formLongitude: PropTypes.number,
  readOnly: PropTypes.bool,
}

export default LocationFields
