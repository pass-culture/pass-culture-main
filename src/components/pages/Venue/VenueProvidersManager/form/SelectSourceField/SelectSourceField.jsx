import React from 'react'
import PropTypes from 'prop-types'
import checkIfProviderShouldBeDisabled from '../../../VenueProvidersManager/utils/checkIfProviderShouldBeDisabled'
import { DEFAULT_PROVIDER_OPTION } from '../../utils/utils'

const SelectSourceField = ({ handleChange, providers, venueProviders }) => ({ input }) => (
  <select
    {...input}
    className="field-select"
    id="provider-options"
    onChange={event => handleChange(event, input)}
  >
    <option
      key={DEFAULT_PROVIDER_OPTION.id}
      value={JSON.stringify(DEFAULT_PROVIDER_OPTION)}
    >
      {DEFAULT_PROVIDER_OPTION.name}
    </option>
    {providers.map((provider) => {
      const isProviderDisabled = checkIfProviderShouldBeDisabled(venueProviders, provider)

      return (
        <option
          disabled={isProviderDisabled}
          key={`provider-${provider.id}`}
          value={JSON.stringify(provider)}
        >
          {provider.name}
        </option>
      )
    })}
  </select>
)

SelectSourceField.propTypes = {
  handleChange: PropTypes.func.isRequired,
  providers: PropTypes.arrayOf(PropTypes.shape()).isRequired,
  venueProviders: PropTypes.arrayOf(PropTypes.shape()).isRequired,
}

export default SelectSourceField
