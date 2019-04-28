import PropTypes from 'prop-types'
import React from 'react'

import AddressField from './AddressField'
import {
  HiddenField,
  NumberField,
  TextField,
} from 'components/layout/form/fields'

const GeoFields = ({
  fieldReadOnlyBecauseFrozenFormSiret,
  form,
  formLatitude,
  formLongitude,
  formSelectedAddress,
  formSiret,
  initialSiret,
  isModifiedEntity,
  latitude,
  longitude,
  readOnly,
}) => {
  const latitudeReadOnlyFromSelectedAddressOrSiren =
    formSelectedAddress !== null ||
    (fieldReadOnlyBecauseFrozenFormSiret && formLatitude !== null)

  const longitudeReadOnlyFromSelectedAddressOrSiren =
    formSelectedAddress !== null ||
    (fieldReadOnlyBecauseFrozenFormSiret && formLongitude !== null)

  const readOnlyFromSelectedAddressOrSiren =
    formSelectedAddress !== null || fieldReadOnlyBecauseFrozenFormSiret

  return (
    <div className="section">
      <h2 className="main-list-title">ADRESSE</h2>
      <div className="field-group">
        <HiddenField name="selectedAddress" />
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
          readOnly={readOnly || readOnlyFromSelectedAddressOrSiren}
          required
        />
        <TextField
          autoComplete="address-level2"
          innerClassName="col-66"
          label="Ville : "
          name="city"
          readOnly={readOnly || readOnlyFromSelectedAddressOrSiren}
          required
        />
        <NumberField
          innerClassName="col-33"
          label="Latitude : "
          name="latitude"
          readOnly={readOnly || latitudeReadOnlyFromSelectedAddressOrSiren}
          required
        />
        <NumberField
          innerClassName="col-33"
          label="Longitude : "
          name="longitude"
          readOnly={readOnly || longitudeReadOnlyFromSelectedAddressOrSiren}
          required
        />
      </div>
    </div>
  )
}

GeoFields.defaultProps = {
  fieldReadOnlyBecauseFrozenFormSiret: false,
  formLatitude: null,
  formLongitude: null,
  formSelectedAddress: null,
  formSiret: null,
  readOnly: true,
}

GeoFields.propTypes = {
  fieldReadOnlyBecauseFrozenFormSiret: PropTypes.bool,
  form: PropTypes.object.isRequired,
  formLatitude: PropTypes.number,
  formLongitude: PropTypes.number,
  formSelectedAddress: PropTypes.string,
  formSiret: PropTypes.string,
  isModifiedEntity: PropTypes.bool.isRequired,
  readOnly: PropTypes.bool,
}

export default GeoFields
