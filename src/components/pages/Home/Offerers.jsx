import React, { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

import Icon from 'components/layout/Icon'
import Select, { buildSelectOptions } from 'components/layout/inputs/Select'
import Spinner from 'components/layout/Spinner'
import * as pcapi from 'repository/pcapi/pcapi'

import { steps, STEP_ID_OFFERERS } from './HomepageBreadcrumb'

const Offerers = () => {
  const [offerers, setOfferers] = useState([])
  const [offererOptions, setOffererOptions] = useState([])
  const [selectedOfferer, setSelectedOfferer] = useState(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(function fetchData() {
    pcapi.getOfferers().then(receivedOfferers => {
      setOfferers(receivedOfferers)
      setOffererOptions(buildSelectOptions('id', 'name', receivedOfferers))
      receivedOfferers.sort((o1, o2) => o1.name.localeCompare(o2.name))
      setSelectedOfferer(receivedOfferers[0])
      setIsLoading(false)
    })
  }, [])

  const handleChangeOfferer = useCallback(
    event => {
      const newOffererId = event.target.value
      if (newOffererId !== selectedOfferer.id) {
        const newSelectedOfferer = offerers.find(offerer => offerer.id === newOffererId)
        setSelectedOfferer(newSelectedOfferer)
      }
    },
    [offerers, selectedOfferer, setSelectedOfferer]
  )

  if (isLoading) {
    return (
      <div className="h-card h-card-secondary h-card-placeholder">
        <div className="h-card-inner">
          <Spinner />
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="h-card h-card-secondary">
        <div className="h-card-inner">
          <div className="h-card-header">
            <div className="h-card-header-block">
              <Select
                handleSelection={handleChangeOfferer}
                id={steps[STEP_ID_OFFERERS].hash}
                name="offererId"
                options={offererOptions}
                selectedValue={selectedOfferer.id}
              />
            </div>
            <div className="h-card-actions">
              <Link
                className="tertiary-button"
                to={`/structures/${selectedOfferer.id}`}
              >
                <Icon svg="ico-outer-pen" />
                {'Modifier'}
              </Link>
            </div>
          </div>
          <div className="h-card-cols">
            <div className="h-card-col">
              <h3 className="h-card-secondary-title">
                {'Informations pratiques'}
              </h3>
              <div className="h-card-content">
                <dl className="h-description-list">
                  <dt>
                    {'Siren :'}
                  </dt>
                  <dd>
                    {selectedOfferer.siren}
                  </dd>

                  <dt>
                    {'Désignation :'}
                  </dt>
                  <dd>
                    {selectedOfferer.name}
                  </dd>

                  <dt>
                    {'Siège social : '}
                  </dt>
                  <dd>
                    {selectedOfferer.address} 
                    {' '}
                    {selectedOfferer.postalCode} 
                    {' '}
                    {selectedOfferer.city}
                  </dd>
                </dl>
              </div>
            </div>

            <div className="h-card-col">
              <h3 className="h-card-secondary-title">
                {'Coordonnées bancaires'}
              </h3>
              <div className="h-card-content h-content-attention">
                {'Hello world !'}
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="h-section-row nested">
        <div className="h-card h-card-primary">
          <div className="h-card-inner">
            <h3 className="h-card-secondary-title">
              {'Votre lieu numérique'}
            </h3>
            <div className="h-card-content">
              {'Hello world !'}
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

export default Offerers
