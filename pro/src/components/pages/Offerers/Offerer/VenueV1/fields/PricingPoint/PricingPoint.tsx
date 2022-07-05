import { Field, useField } from 'react-final-form'
import React, { useEffect, useState } from 'react'

import Button from 'ui-kit/Button/Button'
import { IAPIOfferer } from 'core/Offerers/types'
import { IAPIVenue } from 'core/Venue/types'
import Icon from 'components/layout/Icon'
import { api } from 'apiClient/api'
import styles from './PricingPoint.module.scss'

export interface IPricingPointProps {
  readOnly: boolean
  offerer: IAPIOfferer
  venue: IAPIVenue
}

const PricingPoint = ({ readOnly, offerer, venue }: IPricingPointProps) => {
  const [canSubmit, setCanSubmit] = useState(true)
  const [isInputDisabled, setIsInputDisabled] = useState(false)
  const pricingPointSelectField = useField('venueSiret')

  useEffect(() => {
    setCanSubmit(!pricingPointSelectField.input.value)
  }, [pricingPointSelectField.input.value])

  const handleClick = async () => {
    const pricingPointId = pricingPointSelectField.input.value
    if (venue?.id) {
      api
        .linkVenueToPricingPoint(venue.id, {
          pricingPointId: pricingPointId,
        })
        .then(() => {
          setIsInputDisabled(true)
        })
    }
  }

  return (
    <div className="section vp-content-section bank-information">
      <div className="main-list-title title-actions-container">
        <h2 className="main-list-title-text">Barème de remboursement</h2>
      </div>

      {!readOnly && !venue.pricingPoint && (
        <p className={styles['reimbursement-subtitle']}>
          <span className={styles['text-hightlight']}>
            Sélectionner et valider{' '}
          </span>
          ci-dessous le lieu avec SIRET sur lequel vous souhaitez que vos
          remboursements soient calculés.
        </p>
      )}
      <div className="venue-label-label" id="venue-label">
        <span>
          Lieu avec SIRET utilisé pour le calcul de votre barème de
          remboursement
        </span>
      </div>
      <div className={styles['dropDown-container']}>
        <div className="control control-select">
          <div className={`${styles['select']} select`}>
            <Field
              disabled={
                venue.pricingPoint?.id ? true : isInputDisabled || readOnly
              }
              component="select"
              id="venue-siret"
              name="venueSiret"
              data-testid={'pricingPointSelect'}
              defaultValue={venue.pricingPoint?.id}
            >
              <option value="">Sélectionner un lieu dans la liste</option>
              {offerer.managedVenues.map(
                (venue: IAPIVenue) =>
                  venue?.siret && (
                    <option
                      key={`venue-type-${venue.siret}`}
                      value={venue.nonHumanizedId}
                    >
                      {`${venue.name} - ${venue?.siret}`}
                    </option>
                  )
              )}
            </Field>
          </div>
        </div>
        {!readOnly && !isInputDisabled && (
          <Button
            className={styles['space-left']}
            onClick={handleClick}
            disabled={venue.pricingPoint?.id ? true : canSubmit}
          >
            Valider la sélection
          </Button>
        )}
        {!readOnly && isInputDisabled && (
          <>
            <Icon className={styles['space-left']} svg="ico-valid" />
            <p
              className={styles['space-text-left']}
              data-testid={'validationText'}
            >
              Sélection validée
            </p>
          </>
        )}
      </div>
    </div>
  )
}

export default PricingPoint
