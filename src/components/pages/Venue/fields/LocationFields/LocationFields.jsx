import PropTypes from 'prop-types'
import React from 'react'

import AddressField from './AddressField'
import HiddenField from '../../../../layout/form/fields/HiddenField'
import NumberField from '../../../../layout/form/fields/NumberField'
import TextField from '../../../../layout/form/fields/TextField'

const LocationFields = ({
  fieldReadOnlyBecauseFrozenFormSiret,
  form,
  formLatitude,
  formLongitude,
  formIsLocationFrozen,
  readOnly,
}) => {
  const fieldIsFrozen = readOnly || formIsLocationFrozen || fieldReadOnlyBecauseFrozenFormSiret
  return (
    <div className="section">
      <h2 className="main-list-title">
        {'Adresse'}
      </h2>
      <div className="field-group">
        <HiddenField name="isLocationFrozen" />
        <AddressField
          className="vp-field"
          form={form}
          label="Numéro et voie : "
          latitude={formLatitude}
          longitude={formLongitude}
          name="address"
          readOnly={readOnly || fieldReadOnlyBecauseFrozenFormSiret}
          withMap
        />
        <TextField
          autoComplete="postal-code"
          className="vp-field"
          innerClassName="col-33"
          label="Code postal : "
          name="postalCode"
          readOnly={fieldIsFrozen}
          required
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
        />
        <NumberField
          className="vp-field"
          innerClassName="col-33"
          label="Longitude : "
          name="longitude"
          readOnly={fieldIsFrozen}
          required
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
