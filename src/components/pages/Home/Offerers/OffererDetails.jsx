import PropTypes from 'prop-types'
import React, { useCallback, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import Icon from 'components/layout/Icon'
import Select from 'components/layout/inputs/Select'

import { STEP_ID_OFFERERS, steps } from '../HomepageBreadcrumb'

import BankInformations from "./BankInformations"

const hasBankInformations = offererOrVenue =>
  Boolean((offererOrVenue.iban && offererOrVenue.bic) || offererOrVenue.demarchesSimplifieesApplicationId)

const OffererDetails = ({ handleChangeOfferer, offererOptions, selectedOfferer }) => {
  const [isVisible, setIsVisible] = useState(true)

  const toggleVisibility = useCallback(
    () => setIsVisible(currentVisibility => !currentVisibility),
    []
  )

  const hasMissingBankInformations = useMemo(() => {
    if (!selectedOfferer) return false
    return (
      !hasBankInformations(selectedOfferer) &&
      selectedOfferer.managedVenues.some(venue => !hasBankInformations(venue))
    )
  }, [selectedOfferer])

  return (
    <div className="h-card h-card-secondary">
      <div className="h-card-inner">
        <div className="od-header">
          <div className="od-header-block">
            <Select
              handleSelection={handleChangeOfferer}
              id={steps[STEP_ID_OFFERERS].hash}
              label=""
              name="offererId"
              options={offererOptions}
              selectedValue={selectedOfferer.id}
            />
          </div>
          <div className="od-actions">
            <button
              className="tertiary-button"
              onClick={toggleVisibility}
              type="button"
            >
              <Icon svg="ico-eye-open" />
              {isVisible ? 'Masquer' : 'Afficher'}
            </button>
            {hasMissingBankInformations && (
              <Icon
                alt="Informations bancaires manquantes"
                className="ico-bank-warning"
                svg="ico-alert-filled"
              />
            )}
            <div className="h-separator" />
            <Link
              className="tertiary-link"
              to={`/structures/${selectedOfferer.id}`}
            >
              <Icon svg="ico-outer-pen" />
              {'Modifier'}
            </Link>
          </div>
        </div>
        {isVisible && (
          <div className="h-card-cols">
            <div className="h-card-col">
              <h3 className="h-card-secondary-title">
                {'Informations pratiques'}
              </h3>
              <div className="h-card-content">
                <ul className="h-description-list">
                  <li className="h-dl-row">
                    <span className="h-dl-title">
                      {'Siren :'}
                    </span>
                    <span className="h-dl-description">
                      {selectedOfferer.siren}
                    </span>
                  </li>

                  <li className="h-dl-row">
                    <span className="h-dl-title">
                      {'Désignation :'}
                    </span>
                    <span className="h-dl-description">
                      {selectedOfferer.name}
                    </span>
                  </li>

                  <li className="h-dl-row">
                    <span className="h-dl-title">
                      {'Siège social : '}
                    </span>
                    <span className="h-dl-description">
                      {selectedOfferer.address}
                      {' '}
                      {selectedOfferer.postalCode}
                      {' '}
                      {selectedOfferer.city}
                    </span>
                  </li>
                </ul>
              </div>
            </div>

            <div className="h-card-col">
              <BankInformations
                hasMissingBankInformations={hasMissingBankInformations}
                offerer={selectedOfferer}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

OffererDetails.propTypes = {
  handleChangeOfferer: PropTypes.func.isRequired,
  offererOptions: PropTypes.shape().isRequired,
  selectedOfferer: PropTypes.shape().isRequired,
}

export default OffererDetails
