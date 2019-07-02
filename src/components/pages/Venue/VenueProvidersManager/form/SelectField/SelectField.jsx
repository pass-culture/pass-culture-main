import React from 'react'
import PropTypes from 'prop-types'
import checkIfProviderShouldBeDisabled from '../../../VenueProvidersManager/utils/checkIfProviderShouldBeDisabled'
import { DEFAULT_PROVIDER_OPTION } from '../../utils/utils'

const SelectField = ({
                       handleChange,
                       providers,
                       venueProviders
                     }) =>
  ({input}) => (
    <select
      {...input}
      className="field-select"
      id="provider-options"
      onChange={event => handleChange(event, input)}
    >
      <option key={DEFAULT_PROVIDER_OPTION.id}
              value={JSON.stringify(DEFAULT_PROVIDER_OPTION)}>{DEFAULT_PROVIDER_OPTION.name}
      </option>
      {providers.map((provider, index) => {
        const isProviderDisabled = checkIfProviderShouldBeDisabled(venueProviders, provider)

        return (
          <option disabled={isProviderDisabled}
                  key={index}
                  value={JSON.stringify(provider)}>{provider.name}
          </option>
        )
      })}
    </select>
  )

SelectField.propTypes = {
  handleChange: PropTypes.func.isRequired,
  providers: PropTypes.array.isRequired,
  venueProviders: PropTypes.array.isRequired
}

export default SelectField
