import React, { useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import { OFFER_SUBTYPES, OFFER_TYPES } from 'core/Offers'
import useActiveFeature from 'hooks/useActiveFeature'
import { ReactComponent as CalendarCheckIcon } from 'icons/ico-calendar-check.svg'
import { ReactComponent as CaseIcon } from 'icons/ico-case.svg'
import { ReactComponent as TemplateOfferIcon } from 'icons/ico-template-offer.svg'
import { ReactComponent as PhoneIcon } from 'icons/info-phone.svg'
import { ReactComponent as LibraryIcon } from 'icons/library.svg'
import { ReactComponent as UserIcon } from 'icons/user.svg'

import ActionsBar from './ActionsBar/ActionsBar'
import ActionsBarLegacy from './ActionsBar/ActionsBarLegacy'
import styles from './OfferType.module.scss'
import OfferTypeButton from './OfferTypeButton'
import OldOfferTypeButton from './OldOfferTypeButton'

const OfferType = (): JSX.Element => {
  const history = useHistory()
  const location = useLocation()
  const [offerType, setOfferType] = useState(OFFER_TYPES.INDIVIDUAL_OR_DUO)
  const [offerSubtype, setOfferSubtype] = useState(OFFER_SUBTYPES.COLLECTIVE)
  const isOfferFormV3 = useActiveFeature('OFFER_FORM_V3')
  const isSubtypeChosenAtCreation = useActiveFeature(
    'WIP_CHOOSE_COLLECTIVE_OFFER_TYPE_AT_CREATION'
  )

  const getNextPageHref = () => {
    if (offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO) {
      return history.push({
        pathname: isOfferFormV3
          ? '/offre/v3/creation/individuelle/informations'
          : '/offre/creation/individuel',
        search: location.search,
      })
    }

    // Offer type is EDUCATIONAL
    if (offerSubtype === OFFER_SUBTYPES.TEMPLATE && isSubtypeChosenAtCreation) {
      return history.push({
        pathname: '/offre/creation/collectif/vitrine',
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

  const handleOfferSubtypeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedOfferSubtype = event.target.value as OFFER_SUBTYPES
    setOfferSubtype(selectedOfferSubtype)
  }

  return (
    <div className={styles['offer-type-container']}>
      <h1 className={styles['offer-type-title']}>Créer une offre</h1>
      <FormLayout>
        <FormLayout.Section title="À qui destinez-vous cette offre ? ">
          <FormLayout.Row inline>
            {isSubtypeChosenAtCreation ? (
              <>
                <OfferTypeButton
                  name="offer-type"
                  Icon={PhoneIcon}
                  isSelected={offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO}
                  label="Au grand public"
                  onChange={handleOfferTypeChange}
                  value={OFFER_TYPES.INDIVIDUAL_OR_DUO}
                  className={styles['offer-type-button']}
                />
                <OfferTypeButton
                  name="offer-type"
                  Icon={CaseIcon}
                  isSelected={offerType === OFFER_TYPES.EDUCATIONAL}
                  label="À un groupe scolaire"
                  onChange={handleOfferTypeChange}
                  value={OFFER_TYPES.EDUCATIONAL}
                  className={styles['offer-type-button']}
                />
              </>
            ) : (
              <>
                <OldOfferTypeButton
                  Icon={UserIcon}
                  isSelected={offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO}
                  label="Au grand public"
                  onChange={handleOfferTypeChange}
                  value={OFFER_TYPES.INDIVIDUAL_OR_DUO}
                />
                <OldOfferTypeButton
                  Icon={LibraryIcon}
                  isSelected={offerType === OFFER_TYPES.EDUCATIONAL}
                  label="À un groupe scolaire"
                  onChange={handleOfferTypeChange}
                  value={OFFER_TYPES.EDUCATIONAL}
                />
              </>
            )}
          </FormLayout.Row>
        </FormLayout.Section>

        {offerType === OFFER_TYPES.EDUCATIONAL && isSubtypeChosenAtCreation && (
          <FormLayout.Section title="Quel est le type de l'offre ?">
            <FormLayout.Row inline>
              <OfferTypeButton
                name="offer-subtype"
                Icon={CalendarCheckIcon}
                isSelected={offerSubtype === OFFER_SUBTYPES.COLLECTIVE}
                label="Une offre réservable"
                description="Cette offre a une date et un prix. Vous pouvez choisir de la rendre visible par tous les établissements scolaires ou par un seul."
                onChange={handleOfferSubtypeChange}
                value={OFFER_SUBTYPES.COLLECTIVE}
              />
            </FormLayout.Row>
            <FormLayout.Row inline>
              <OfferTypeButton
                name="offer-subtype"
                Icon={TemplateOfferIcon}
                isSelected={offerSubtype === OFFER_SUBTYPES.TEMPLATE}
                label="Une offre vitrine"
                description="Cette offre n’est pas réservable. Elle n’a ni date, ni prix et permet aux enseignants de vous contacter pour co-construire une offre adaptée. "
                onChange={handleOfferSubtypeChange}
                value={OFFER_SUBTYPES.TEMPLATE}
              />
            </FormLayout.Row>
          </FormLayout.Section>
        )}

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
