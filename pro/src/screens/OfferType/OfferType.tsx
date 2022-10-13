import React, { useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import { OFFER_TYPES } from 'core/Offers'
import useActiveFeature from 'hooks/useActiveFeature'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'
import FormLayout from 'new_components/FormLayout'

import ActionsBar from './ActionsBar/ActionsBar'
import ActionsBarLegacy from './ActionsBar/ActionsBarLegacy'
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

        {isOfferFormV3 ? (
          <ActionsBar getNextPageHref={getNextPageHref} />
        ) : (
          <ActionsBarLegacy getNextPageHref={getNextPageHref} />
        )}
      </FormLayout>
    </div>
  )
}

export default OfferType
