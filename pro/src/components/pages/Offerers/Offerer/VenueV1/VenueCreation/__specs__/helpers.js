import { screen } from '@testing-library/dom'
import { waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'

import fetchAddressData from 'components/pages/Offerers/Offerer/VenueV1/fields/LocationFields/utils/fetchAddressData'

export const fieldLabels = {
  siret: {
    labelCreation: 'SIRET du lieu qui accueille vos offres (si applicable) :',
    label: 'SIRET :',
    exact: false,
    type: 'text',
  },
  name: { label: 'Nom du lieu', exact: false, type: 'text' },
  publicName: { label: 'Nom d’usage du lieu', exact: false, type: 'text' },
  bookingEmail: { label: 'Mail : *', exact: false, type: 'text' },
  comment: { label: 'Commentaire', exact: false, type: 'text' },
  address: { label: 'Numéro et voie', exact: false, type: 'text' },
  city: { label: 'Ville', exact: false, type: 'text' },
  postalCode: { label: 'Code postal', exact: false, type: 'text' },
  longitude: { label: 'Longitude', exact: false, type: 'text' },
  latitude: { label: 'Latitude', exact: false, type: 'text' },
  venueTypeCode: { label: 'Type de lieu', exact: false, type: 'select' },
  venueLabelId: {
    label: 'Label du Ministère de la Culture ou du CNC',
    exact: false,
    type: 'select',
  },
  noDisabilityCompliant: {
    label: 'Non accessible',
    exact: false,
    type: 'checkbox',
  },
  audioDisabilityCompliant: {
    label: 'Auditif',
    exact: false,
    type: 'checkbox',
  },
  motorDisabilityCompliant: {
    label: 'Moteur',
    exact: false,
    type: 'checkbox',
  },
  mentalDisabilityCompliant: {
    label: 'Psychique ou cognitif',
    exact: false,
    type: 'checkbox',
  },
  visualDisabilityCompliant: {
    label: 'Visuel',
    exact: false,
    type: 'checkbox',
  },
  description: { label: 'Description', exact: false, type: 'text' },
}

export const findVenueInputForField = async (fieldName, isCreatedEntity) => {
  const { label, exact } = fieldLabels[fieldName]
  if (fieldName === 'siret' && isCreatedEntity) {
    const { labelCreation } = fieldLabels[fieldName]
    return await screen.findByLabelText(labelCreation, { exact })
  }
  return await screen.findByLabelText(label, { exact })
}

export const queryVenueInputForField = (fieldName, isCreatedEntity) => {
  const { label, exact } = fieldLabels[fieldName]
  if (fieldName === 'siret' && isCreatedEntity) {
    const { labelCreation } = fieldLabels[fieldName]
    return screen.queryByLabelText(labelCreation, { exact })
  }
  return screen.queryByLabelText(label, { exact })
}

export const setVenueAddress = async addressDetails => {
  const dropdownAddressValue = `${addressDetails['address']} ${addressDetails['postalCode']} ${addressDetails['city']}`
  fetchAddressData.mockReturnValue([
    {
      address: addressDetails['address'],
      city: addressDetails['city'],
      id: 'api address fake id',
      label: dropdownAddressValue,
      latitude: addressDetails['latitude'],
      longitude: addressDetails['longitude'],
      postalCode: addressDetails['postalCode'],
    },
  ])
  const addressField = await findVenueInputForField('address')
  const cityField = await findVenueInputForField('city')
  const postalCodeField = await findVenueInputForField('postalCode')
  const longitudeField = await findVenueInputForField('longitude')
  const latitudeField = await findVenueInputForField('latitude')

  await userEvent.type(addressField, addressDetails['address'])

  const apiAddressUrl = `https://api-adresse.data.gouv.fr/search/?limit=5&q=${addressDetails['address']}`
  await waitFor(() => {
    expect(fetchAddressData).toHaveBeenCalledWith(apiAddressUrl)
  })
  const dropdownAddress = await screen.findByText(dropdownAddressValue, {
    selector: '.location-viewer div',
    exact: false,
  })
  dropdownAddress.click()

  await waitFor(() => {
    expect(cityField).toHaveValue(addressDetails['city'])
    expect(postalCodeField).toHaveValue(addressDetails['postalCode'].toString())
    expect(longitudeField).toHaveValue(addressDetails['longitude'].toString())
    expect(latitudeField).toHaveValue(addressDetails['latitude'].toString())
  })

  return Promise.resolve({
    address: addressField,
    city: cityField,
    postalCode: postalCodeField,
    longitude: longitudeField,
    latitude: latitudeField,
  })
}

export const setVenueValues = async values => {
  const addressFields = [
    'address',
    'city',
    'postalCode',
    'latitude',
    'longitude',
  ]

  const setFormValueForField = async (field, value) => {
    const { label, exact, type } = fieldLabels[field]
    const input = screen.getByLabelText(label, { exact })

    if (type === 'checkbox') {
      await userEvent.click(input)
    } else if (type === 'select') {
      await userEvent.selectOptions(input, value)
      await waitFor(() => expect(input).toHaveValue(value))
    } else {
      await userEvent.type(input, value)
    }
    return Promise.resolve(input)
  }

  let modifiedInputs = {}
  for (const fieldName in values) {
    if (!addressFields.includes(fieldName)) {
      modifiedInputs[fieldName] = await setFormValueForField(
        fieldName,
        values[fieldName]
      )
    }
  }

  const hasAddressValues = valueFields =>
    valueFields.filter(field => addressFields.includes(field)).length > 0
  if (hasAddressValues(Object.keys(values))) {
    modifiedInputs = {
      ...modifiedInputs,
      ...(await setVenueAddress({
        address: values['address'] || '',
        city: values['city'] || '',
        postalCode: values['postalCode'] || '',
        latitude: values['latitude'] || '',
        longitude: values['longitude'] || '',
      })),
    }
  }
  // return await Promise.all(modifiedInputs)
  return Promise.resolve(modifiedInputs)
}
