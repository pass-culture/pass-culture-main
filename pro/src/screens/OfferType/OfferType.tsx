import React, { useState } from 'react'
import { Link, useHistory, useLocation } from 'react-router-dom'

import useActiveFeature from 'components/hooks/useActiveFeature'
import { OFFER_TYPES } from 'core/Offers'
import { computeOffersUrl } from 'core/Offers/utils'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'
import FormLayout from 'new_components/FormLayout'
import { SubmitButton } from 'ui-kit'

import styles from './OfferType.module.scss'
import OfferTypeButton from './OfferTypeButton'

const { INDIVIDUAL_OR_DUO, EDUCATIONAL } = OFFER_TYPES

const OfferType = (): JSX.Element => {
  const history = useHistory()
  const location = useLocation()
  const [offerType, setOfferType] = useState(INDIVIDUAL_OR_DUO)
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')

  const getNextPageHref = () => {
    if (offerType === INDIVIDUAL_OR_DUO) {
      return history.push({
        pathname: isOfferFormV3
          ? '/offre/v3/creation/individuelle/informations'
          : '/offre/creation/individuel',
        search: location.search,
      })
    }
    return history.push({
      pathname: '/offre/creation/collectif',
      search: location.search,
    })
  }

  const handleOfferTypeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedOfferType = event.target.value as OFFER_TYPES
    setOfferType(selectedOfferType)
  }

  return (
    <div>
      <h1 className={styles['offer-type-title']}>Créer une offre</h1>
      <FormLayout>
        <FormLayout.Section title="À qui destinez-vous cette offre ? ">
          <FormLayout.Row inline>
            <OfferTypeButton
              Icon={UserIcon}
              isSelected={offerType === INDIVIDUAL_OR_DUO}
              label="Au grand public"
              onChange={handleOfferTypeChange}
              value={INDIVIDUAL_OR_DUO}
            />
            <OfferTypeButton
              Icon={LibraryIcon}
              isSelected={offerType === EDUCATIONAL}
              label="À un groupe scolaire"
              onChange={handleOfferTypeChange}
              value={EDUCATIONAL}
            />
          </FormLayout.Row>
        </FormLayout.Section>

        <FormLayout.Actions>
          <Link className="secondary-link" to={computeOffersUrl({})}>
            Retour
          </Link>
          <SubmitButton
            className="primary-button"
            disabled={false}
            isLoading={false}
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
