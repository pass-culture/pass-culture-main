import PropTypes from 'prop-types'
import React from 'react'

import AddressField from './AddressField'
import {
  HiddenField,
  NumberField,
  TextField,
} from 'components/layout/form/fields'

const LocationFields = ({
  fieldReadOnlyBecauseFrozenFormSiret,
  form,
  formLatitude,
  formLongitude,
  formIsLocationFrozen,
  readOnly,
}) => {
  const readOnlyFromAddressOrSiren = formIsLocationFrozen || fieldReadOnlyBecauseFrozenFormSiret
  const fieldReadOnly = readOnly || readOnlyFromAddressOrSiren

  return (
    <div className="section">
      <h2 className="main-list-title">ADRESSE</h2>
      <div className="field-group">
        <HiddenField name="isLocationFrozen" />
        <AddressField
          form={form}
          label="Numéro et voie : "
          latitude={formLatitude}
          longitude={formLongitude}
          name="address"
          readOnly={readOnly || fieldReadOnlyBecauseFrozenFormSiret}
          required
          withMap
        />
        <TextField
          autoComplete="postal-code"
          innerClassName="col-33"
          label="Code postal : "
          name="postalCode"
          readOnly={fieldReadOnly}
          required
        />
        <TextField
          autoComplete="address-level2"
          innerClassName="col-66"
          label="Ville : "
          name="city"
          readOnly={fieldReadOnly}
          required
        />
        <NumberField
          innerClassName="col-33"
          label="Latitude : "
          name="latitude"
          readOnly={fieldReadOnly}
          required
        />
        <NumberField
          innerClassName="col-33"
          label="Longitude : "
          name="longitude"
          readOnly={fieldReadOnly}
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
  form: PropTypes.object.isRequired,
  formIsLocationFrozen: PropTypes.bool,
  formLatitude: PropTypes.number,
  formLongitude: PropTypes.number,
  readOnly: PropTypes.bool,
}

export default LocationFields
