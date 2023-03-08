import React, { FormEvent, useCallback, useState } from 'react'
import { useHistory, useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import FormLayout from 'components/FormLayout'
import { OFFER_WIZARD_STEP_IDS } from 'components/OfferIndividualBreadcrumb'
import PageTitle from 'components/PageTitle/PageTitle'
import {
  Events,
  OFFER_FORM_HOMEPAGE,
  OFFER_FORM_NAVIGATION_MEDIUM,
} from 'core/FirebaseEvents/constants'
import canOffererCreateCollectiveOfferAdapter from 'core/OfferEducational/adapters/canOffererCreateCollectiveOfferAdapter'
import {
  INDIVIDUAL_OFFER_SUBTYPE,
  COLLECTIVE_OFFER_SUBTYPE,
  OFFER_TYPES,
  OFFER_WIZARD_MODE,
} from 'core/Offers'
import {
  COLLECTIVE_OFFER_SUBTYPE_DUPLICATE,
  DEFAULT_SEARCH_FILTERS,
} from 'core/Offers/constants'
import { getOfferIndividualUrl } from 'core/Offers/utils/getOfferIndividualUrl'
import useActiveFeature from 'hooks/useActiveFeature'
import useAnalytics from 'hooks/useAnalytics'
import useCurrentUser from 'hooks/useCurrentUser'
import useNotification from 'hooks/useNotification'
import { ReactComponent as CalendarCheckIcon } from 'icons/ico-calendar-check.svg'
import { ReactComponent as CaseIcon } from 'icons/ico-case.svg'
import { ReactComponent as DateIcon } from 'icons/ico-date.svg'
import { ReactComponent as DuplicateOfferIcon } from 'icons/ico-duplicate-offer.svg'
import { ReactComponent as NewOfferIcon } from 'icons/ico-new-offer.svg'
import { ReactComponent as TemplateOfferIcon } from 'icons/ico-template-offer.svg'
import { ReactComponent as ThingIcon } from 'icons/ico-thing.svg'
import { ReactComponent as VirtualEventIcon } from 'icons/ico-virtual-event.svg'
import { ReactComponent as VirtualThingIcon } from 'icons/ico-virtual-thing.svg'
import { ReactComponent as PhoneIcon } from 'icons/info-phone.svg'
import { getFilteredCollectiveOffersAdapter } from 'pages/CollectiveOffers/adapters'
import { Banner } from 'ui-kit'
import RadioButtonWithImage from 'ui-kit/RadioButtonWithImage'
import Spinner from 'ui-kit/Spinner/Spinner'

import ActionsBar from './ActionsBar/ActionsBar'
import styles from './OfferType.module.scss'

const OfferType = (): JSX.Element => {
  const history = useHistory()
  const location = useLocation()
  const notify = useNotification()
  const { logEvent } = useAnalytics()
  const isDuplicateOfferSelectionActive = useActiveFeature(
    'WIP_DUPLICATE_OFFER_SELECTION'
  )
  const [offerType, setOfferType] = useState(OFFER_TYPES.INDIVIDUAL_OR_DUO)
  const [collectiveOfferSubtype, setCollectiveOfferSubtype] = useState(
    COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE
  )
  const [collectiveOfferSubtypeDuplicate, setCollectiveOfferSubtypeDuplicate] =
    useState(COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER)
  const [individualOfferSubtype, setIndividualOfferSubtype] = useState(
    INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
  )
  const [hasCollectiveTemplateOffer, setHasCollectiveTemplateOffer] =
    useState(false)
  const queryParams = new URLSearchParams(location.search)
  const queryOffererId = queryParams.get('structure')
  const queryVenueId = queryParams.get('lieu')
  const getTemplateCollectiveOffers = useCallback(async () => {
    const apiFilters = {
      ...DEFAULT_SEARCH_FILTERS,
      collectiveOfferType: COLLECTIVE_OFFER_SUBTYPE.TEMPLATE.toLowerCase(),
      offererId: queryOffererId ?? 'all',
      venueId: queryVenueId ?? 'all',
    }
    const { isOk, message, payload } = await getFilteredCollectiveOffersAdapter(
      apiFilters
    )

    if (!isOk) {
      setHasCollectiveTemplateOffer(false)
      return notify.error(message)
    }

    if (payload.offers.length > 0) {
      setHasCollectiveTemplateOffer(true)
    }
  }, [offerType])
  const [isLoadingEligibility, setIsLoadingEligibility] = useState(false)
  const [isEligible, setIsEligible] = useState(false)
  const { currentUser } = useCurrentUser()

  const getNextPageHref = (event: FormEvent<HTMLFormElement>) => {
    if (offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO) {
      logEvent?.(Events.CLICKED_OFFER_FORM_NAVIGATION, {
        offerType: individualOfferSubtype,
        to: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
        from: OFFER_FORM_HOMEPAGE,
        used: OFFER_FORM_NAVIGATION_MEDIUM.STICKY_BUTTONS,
      })
      /* istanbul ignore next: condition will be removed when FF active in prod */
      return history.push({
        pathname: getOfferIndividualUrl({
          step: OFFER_WIZARD_STEP_IDS.INFORMATIONS,
          mode: OFFER_WIZARD_MODE.CREATION,
        }),
        search: `${location.search}${
          location.search ? '&' : '?'
        }offer-type=${individualOfferSubtype}`,
      })
    }
    // Offer type is EDUCATIONAL
    if (collectiveOfferSubtype === COLLECTIVE_OFFER_SUBTYPE.TEMPLATE) {
      return history.push({
        pathname: '/offre/creation/collectif/vitrine',
        search: location.search,
      })
    }
    if (
      collectiveOfferSubtypeDuplicate ===
      COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE
    ) {
      if (!hasCollectiveTemplateOffer) {
        event.preventDefault()
        return notify.error(
          'Vous devez créer une offre vitrine avant de pouvoir utiliser cette fonctionnalité'
        )
      }
      return history.push({
        pathname: '/offre/creation/collectif/selection',
        search: location.search,
      })
    }

    return history.push({
      pathname: '/offre/creation/collectif',
      search: location.search,
    })
  }

  const checkOffererEligibility = async () => {
    setIsLoadingEligibility(true)
    const offererNames = await api.listOfferersNames()

    const offererId = currentUser.isAdmin
      ? queryOffererId
      : offererNames.offerersNames[0].id
    if (offererNames.offerersNames.length > 1) {
      setIsEligible(true)
    }
    if (offererId) {
      const { isOk, message, payload } =
        await canOffererCreateCollectiveOfferAdapter(offererId)

      if (!isOk) {
        notify.error(message)
      }
      setIsEligible(payload.isOffererEligibleToEducationalOffer)
    }
    setIsLoadingEligibility(false)
  }

  const handleOfferTypeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedOfferType = event.target.value as OFFER_TYPES
    setOfferType(selectedOfferType)
    if (
      isDuplicateOfferSelectionActive &&
      selectedOfferType === OFFER_TYPES.EDUCATIONAL
    ) {
      getTemplateCollectiveOffers()
      checkOffererEligibility()
    }
  }

  const handleCollectiveOfferSubtypeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedCollectiveOfferSubtype = event.target
      .value as COLLECTIVE_OFFER_SUBTYPE
    setCollectiveOfferSubtype(selectedCollectiveOfferSubtype)
  }

  const handleCollectiveOfferSubtypeDuplicateChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedCollectiveOfferSubtypeDuplicate = event.target
      .value as COLLECTIVE_OFFER_SUBTYPE_DUPLICATE
    setCollectiveOfferSubtypeDuplicate(selectedCollectiveOfferSubtypeDuplicate)
  }

  const handleIndividualOfferSubtypeChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedIndividualOfferSubtype = event.target
      .value as INDIVIDUAL_OFFER_SUBTYPE
    setIndividualOfferSubtype(selectedIndividualOfferSubtype)
  }

  return (
    <div className={styles['offer-type-container']}>
      <PageTitle title="Nature de l'offre" />
      <h1 className={styles['offer-type-title']}>Créer une offre</h1>
      <form onSubmit={getNextPageHref}>
        <FormLayout>
          <FormLayout.Section title="À qui destinez-vous cette offre ?">
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

          {offerType === OFFER_TYPES.EDUCATIONAL &&
            (isEligible || !isDuplicateOfferSelectionActive) &&
            !isLoadingEligibility && (
              <FormLayout.Section
                title="Quel est le type de l’offre ?"
                className={styles['subtype-section']}
              >
                <FormLayout.Row inline mdSpaceAfter>
                  <RadioButtonWithImage
                    name="offer-subtype"
                    Icon={CalendarCheckIcon}
                    isChecked={
                      collectiveOfferSubtype ===
                      COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE
                    }
                    label="Une offre réservable"
                    description="Cette offre a une date et un prix. Vous pouvez choisir de la rendre visible par tous les établissements scolaires ou par un seul."
                    onChange={handleCollectiveOfferSubtypeChange}
                    value={COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE}
                  />
                </FormLayout.Row>

                <FormLayout.Row inline mdSpaceAfter>
                  <RadioButtonWithImage
                    name="offer-subtype"
                    Icon={TemplateOfferIcon}
                    isChecked={
                      collectiveOfferSubtype ===
                      COLLECTIVE_OFFER_SUBTYPE.TEMPLATE
                    }
                    label="Une offre vitrine"
                    description={`Cette offre n’est pas réservable. Elle n’a ni date, ni prix et permet aux enseignants de vous contacter pour co-construire une offre adaptée.${
                      isDuplicateOfferSelectionActive &&
                      ' Vous pourrez facilement la dupliquer pour chaque enseignant intéressé.'
                    }`}
                    onChange={handleCollectiveOfferSubtypeChange}
                    value={COLLECTIVE_OFFER_SUBTYPE.TEMPLATE}
                  />
                </FormLayout.Row>
              </FormLayout.Section>
            )}
          {offerType === OFFER_TYPES.INDIVIDUAL_OR_DUO && (
            <FormLayout.Section
              title="Quel est le type de l’offre ?"
              className={styles['subtype-section']}
            >
              <FormLayout.Row inline mdSpaceAfter>
                <RadioButtonWithImage
                  className={styles['individual-radio-button']}
                  name="offer-subtype"
                  Icon={ThingIcon}
                  isChecked={
                    individualOfferSubtype ===
                    INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
                  }
                  label="Un bien physique"
                  description="Livre, instrument de musique, abonnement, cartes et pass…"
                  onChange={handleIndividualOfferSubtypeChange}
                  value={INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD}
                  dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD}`}
                />
              </FormLayout.Row>

              <FormLayout.Row inline mdSpaceAfter>
                <RadioButtonWithImage
                  className={styles['individual-radio-button']}
                  name="offer-subtype"
                  Icon={VirtualThingIcon}
                  isChecked={
                    individualOfferSubtype ===
                    INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD
                  }
                  label="Un bien numérique"
                  description="Ebook, jeu vidéo, abonnement streaming..."
                  onChange={handleIndividualOfferSubtypeChange}
                  value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD}
                  dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD}`}
                />
              </FormLayout.Row>

              <FormLayout.Row inline mdSpaceAfter>
                <RadioButtonWithImage
                  className={styles['individual-radio-button']}
                  name="offer-subtype"
                  Icon={DateIcon}
                  isChecked={
                    individualOfferSubtype ===
                    INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT
                  }
                  label="Un évènement physique daté"
                  description="Concert, représentation, conférence, ateliers..."
                  onChange={handleIndividualOfferSubtypeChange}
                  value={INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT}
                  dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT}`}
                />
              </FormLayout.Row>

              <FormLayout.Row inline mdSpaceAfter>
                <RadioButtonWithImage
                  className={styles['individual-radio-button']}
                  name="offer-subtype"
                  Icon={VirtualEventIcon}
                  isChecked={
                    individualOfferSubtype ===
                    INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT
                  }
                  label="Un évènement numérique daté"
                  description="Livestream, cours en ligne, conférence en ligne..."
                  onChange={handleIndividualOfferSubtypeChange}
                  value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}
                  dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}`}
                />
              </FormLayout.Row>
            </FormLayout.Section>
          )}

          {isDuplicateOfferSelectionActive &&
            isEligible &&
            !isLoadingEligibility &&
            offerType === OFFER_TYPES.EDUCATIONAL &&
            collectiveOfferSubtype === COLLECTIVE_OFFER_SUBTYPE.COLLECTIVE && (
              <FormLayout.Section
                title="Créer une nouvelle offre ou dupliquer une offre ?"
                className={styles['subtype-section']}
              >
                <FormLayout.Row inline mdSpaceAfter>
                  <RadioButtonWithImage
                    name="offer-duplicate"
                    Icon={NewOfferIcon}
                    isChecked={
                      collectiveOfferSubtypeDuplicate ===
                      COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER
                    }
                    label="Créer une nouvelle offre"
                    description="Créer une nouvelle offre réservable en partant d’un formulaire vierge."
                    onChange={handleCollectiveOfferSubtypeDuplicateChange}
                    value={COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.NEW_OFFER}
                  />
                </FormLayout.Row>
                <FormLayout.Row inline mdSpaceAfter>
                  <RadioButtonWithImage
                    name="offer-duplicate"
                    transparent
                    Icon={DuplicateOfferIcon}
                    isChecked={
                      collectiveOfferSubtypeDuplicate ===
                      COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE
                    }
                    label="Dupliquer les informations d’une d’offre vitrine"
                    description="Créez une offre réservable en dupliquant les informations d’une offre vitrine existante."
                    onChange={handleCollectiveOfferSubtypeDuplicateChange}
                    value={COLLECTIVE_OFFER_SUBTYPE_DUPLICATE.DUPLICATE}
                  />
                </FormLayout.Row>
              </FormLayout.Section>
            )}

          {isLoadingEligibility && <Spinner />}
          {offerType === OFFER_TYPES.EDUCATIONAL &&
            !isEligible &&
            !isLoadingEligibility &&
            isDuplicateOfferSelectionActive && (
              <Banner
                links={[
                  {
                    href: 'https://passculture.typeform.com/to/VtKospEg',
                    linkTitle: 'Faire une demande de référencement',
                  },
                  {
                    href: 'https://aide.passculture.app/hc/fr/articles/5700215550364',
                    linkTitle:
                      'Ma demande de référencement a été acceptée mais je ne peux toujours pas créer d’offres collectives',
                  },
                ]}
              >
                Pour proposer des offres à destination d’un groupe scolaire,
                vous devez être référencé auprès du ministère de l’Éducation
                Nationale et du ministère de la Culture.
              </Banner>
            )}
          <ActionsBar
            disableNextButton={
              offerType === OFFER_TYPES.EDUCATIONAL &&
              !isEligible &&
              isDuplicateOfferSelectionActive
            }
          />
        </FormLayout>
      </form>
    </div>
  )
}

export default OfferType
