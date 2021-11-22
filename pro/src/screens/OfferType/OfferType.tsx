import React, { useState, useReducer } from 'react'
import { Link, useHistory, useLocation } from 'react-router-dom'

import Banner from 'components/layout/Banner/Banner'
import { computeOffersUrl } from 'components/pages/Offers/utils/computeOffersUrl'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'
import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'

import { OFFER_TYPES } from './constants'
import styles from './OfferType.module.scss'
import OfferTypeButton from './OfferTypeButton'
import {
  FAILURE_ACTION,
  FETCH_ACTION,
  initialState,
  reducer,
  SUCCESS_ACTION,
} from './utils/fetchEligibilityReducer'

const { INDIVIDUAL_OR_DUO, EDUCATIONAL } = OFFER_TYPES

export interface IOfferTypeProps {
  fetchCanOffererCreateEducationalOffer: () => void
}

const OfferType = ({
  fetchCanOffererCreateEducationalOffer,
}: IOfferTypeProps): JSX.Element => {
  const history = useHistory()
  const location = useLocation()
  const [offerType, setOfferType] = useState(INDIVIDUAL_OR_DUO)
  const [{ hasBeenCalled, isEligible, isLoading }, dispatch] = useReducer(
    reducer,
    initialState
  )

  const getNextPageHref = () => {
    if (offerType === INDIVIDUAL_OR_DUO) {
      return history.push({
        pathname: '/offres/creation',
        search: location.search,
      })
    }

    return history.push({
      pathname: '/offre/creation/scolaire',
      search: location.search,
    })
  }

  const handleOfferTypeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedOfferType = event.target.value as OFFER_TYPES
    setOfferType(selectedOfferType)
  }

  const handleEducationalClick = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    handleOfferTypeChange(event)

    if (!hasBeenCalled) {
      dispatch(FETCH_ACTION)
      try {
        await fetchCanOffererCreateEducationalOffer()
        dispatch(SUCCESS_ACTION)
      } catch (e) {
        dispatch(FAILURE_ACTION)
      }
    }
  }

  return (
    <div>
      <h1 className={styles['offer-type-title']}>Créer une nouvelle offre</h1>
      <FormLayout>
        <FormLayout.Section title="Quel type d’offre souhaitez-vous proposer ?">
          <FormLayout.Row inline>
            <OfferTypeButton
              Icon={UserIcon}
              isSelected={offerType === INDIVIDUAL_OR_DUO}
              label="Une offre à destination du grand public"
              onChange={handleOfferTypeChange}
              value={INDIVIDUAL_OR_DUO}
            />
            <OfferTypeButton
              Icon={LibraryIcon}
              disabled={isEligible === false}
              isSelected={offerType === EDUCATIONAL}
              label="Une offre à destination d'un groupe scolaire"
              onChange={handleEducationalClick}
              value={EDUCATIONAL}
            />
          </FormLayout.Row>
          {isEligible === false ? (
            <Banner href="#" linkTitle="Faire une demande de référencement">
              Pour proposer des offres à destination d’un groupe scolaire, vous
              devez être référencé auprès du ministère de l’Éducation Nationale
              et du ministère de la Culture.
            </Banner>
          ) : null}
        </FormLayout.Section>

        <FormLayout.Actions>
          <Link className="secondary-link" to={computeOffersUrl({})}>
            Retour
          </Link>
          <SubmitButton
            className="primary-button"
            disabled={isEligible === false && offerType === EDUCATIONAL}
            isLoading={isLoading}
            onClick={getNextPageHref}
          >
            Étape suivante
          </SubmitButton>
        </FormLayout.Actions>
      </FormLayout>
    </div>
  )
}

export default OfferType
