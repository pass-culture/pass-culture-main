import React, { useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualStepper'
import PageTitle from 'components/PageTitle/PageTitle'
import {
  COLLECTIVE_OFFER_SUBTYPE,
  OFFER_TYPES,
  OFFER_WIZARD_MODE,
} from 'core/Offers'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import { ReactComponent as CalendarCheckIcon } from 'icons/ico-calendar-check.svg'
import { ReactComponent as CaseIcon } from 'icons/ico-case.svg'
import { ReactComponent as TemplateOfferIcon } from 'icons/ico-template-offer.svg'
import { ReactComponent as PhoneIcon } from 'icons/info-phone.svg'
import RadioButtonWithImage from 'ui-kit/RadioButtonWithImage'

import ActionsBar from './ActionsBar/ActionsBar'
import styles from './OfferType.module.scss'

const OfferType = (): JSX.Element => {
  const history = useHistory()
  const location = useLocation()
  const [offerType, setOfferType] = useState(OFFER_TYPES.INDIVIDUAL_OR_DUO)
  const [offerSubtype, setOfferSubtype] = useState(
    COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE
  )

  const getNextPageHref = () => {
    if (offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO) {
      /* istanbul ignore next: condition will be removed when FF active in prod */
      return history.push({
        pathname: getOfferIndividualUrl({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
        }),
        search: location.search,
      })
    }

    // Offer type is EDUCATIONAL
    if (offerSubtype === COLLECTIVE_OFFER_SUBTYPE.TEMPLATE) {
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
    const selectedOfferSubtype = event.target.value as COLLECTIVE_OFFER_SUBTYPE
    setOfferSubtype(selectedOfferSubtype)
  }

  return (
    <div className={styles['offer-type-container']}>
      <PageTitle title="Nature de l'offre" />
      <h1 className={styles['offer-type-title']}>Créer une offre</h1>
      <FormLayout>
        <FormLayout.Section title="À qui destinez-vous cette offre ? ">
          <FormLayout.Row inline>
            <RadioButtonWithImage
              name="offer-type"
              Icon={PhoneIcon}
              isChecked={offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO}
              label="Au grand public"
              onChange={handleOfferTypeChange}
              value={OFFER_TYPES.INDIVIDUAL_OR_DUO}
              className={styles['offer-type-button']}
            />
            <RadioButtonWithImage
              name="offer-type"
              Icon={CaseIcon}
              isChecked={offerType === OFFER_TYPES.EDUCATIONAL}
              label="À un groupe scolaire"
              onChange={handleOfferTypeChange}
              value={OFFER_TYPES.EDUCATIONAL}
              className={styles['offer-type-button']}
            />
          </FormLayout.Row>
        </FormLayout.Section>

        {offerType === OFFER_TYPES.EDUCATIONAL && (
          <FormLayout.Section
            title="Quel est le type de l’offre ?"
            className={styles['subtype-section']}
          >
            <FormLayout.Row inline>
              <RadioButtonWithImage
                name="offer-subtype"
                Icon={CalendarCheckIcon}
                isChecked={offerSubtype === COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE}
                label="Une offre réservable"
                description="Cette offre a une date et un prix. Vous pouvez choisir de la rendre visible par tous les établissements scolaires ou par un seul."
                onChange={handleOfferSubtypeChange}
                value={COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE}
              />
            </FormLayout.Row>
            <FormLayout.Row inline>
              <RadioButtonWithImage
                name="offer-subtype"
                Icon={TemplateOfferIcon}
                isChecked={offerSubtype === COLLECTIVE_OFFER_SUBTYPE.TEMPLATE}
                label="Une offre vitrine"
                description="Cette offre n’est pas réservable. Elle n’a ni date, ni prix et permet aux enseignants de vous contacter pour co-construire une offre adaptée. "
                onChange={handleOfferSubtypeChange}
                value={COLLECTIVE_OFFER_SUBTYPE.TEMPLATE}
              />
            </FormLayout.Row>
          </FormLayout.Section>
        )}

        <ActionsBar getNextPageHref={getNextPageHref} />
      </FormLayout>
    </div>
  )
}

export default OfferType
