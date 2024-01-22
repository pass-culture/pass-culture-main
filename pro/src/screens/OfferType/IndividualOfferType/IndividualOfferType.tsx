import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { api } from 'apiClient/api'
import { SubcategoryIdEnum, SubcategoryResponseModel } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers/constants'
import { getIndividualOfferVenuesAdapter } from 'core/Venue/adapters/getIndividualOfferVenuesAdapter'
import { getVenueAdapter } from 'core/Venue/adapters/getVenueAdapter'
import useCurrentUser from 'hooks/useCurrentUser'
import useNewIndividualOfferType from 'hooks/useNewIndividualOfferType'
import strokeDateIcon from 'icons/stroke-date.svg'
import thingStrokeIcon from 'icons/stroke-thing.svg'
import strokeVirtualEventIcon from 'icons/stroke-virtual-event.svg'
import strokeVirtualThingIcon from 'icons/stroke-virtual-thing.svg'
import { RadioButton } from 'ui-kit'
import { BaseRadioVariant } from 'ui-kit/form/shared/BaseRadio/types'
import RadioButtonWithImage from 'ui-kit/RadioButtonWithImage'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sendSentryCustomError } from 'utils/sendSentryError'

import styles from '../OfferType.module.scss'
import { OfferTypeFormValues } from '../types'

import { venueTypeSubcategoriesMapping } from './venueTypeSubcategoriesMapping'

async function getCategories() {
  try {
    const categories = await api.getCategories()
    return categories
  } catch (e) {
    sendSentryCustomError(`error when fetching categories ${e}`)

    return null
  }
}

const getVenueTypeAndSubcategories = async (
  venueId: string | null,
  offererId: string | null
): Promise<[string | null, SubcategoryResponseModel[]]> => {
  let venueType: string | null = null
  let subcategories: SubcategoryResponseModel[] = []

  if (venueId) {
    const [categoriesResponse, venueResponse] = await Promise.all([
      getCategories(),
      getVenueAdapter(Number(venueId)),
    ])

    if (venueResponse.isOk && categoriesResponse) {
      const venueData = venueResponse.payload
      venueType = venueData.venueType
      subcategories = categoriesResponse.subcategories
    }
  } else {
    const [categoriesResponse, venuesResponse] = await Promise.all([
      getCategories(),
      getIndividualOfferVenuesAdapter({
        offererId: offererId ? Number(offererId) : undefined,
      }),
    ])

    if (venuesResponse.isOk && categoriesResponse) {
      const venuesData = venuesResponse.payload.filter(
        (venue) => !venue.isVirtual
      )

      if (venuesData.length === 1) {
        venueType = venuesData[0].venueType
        subcategories = categoriesResponse.subcategories
      }
    }
  }
  return [venueType, subcategories]
}

const IndividualOfferType = (): JSX.Element | null => {
  const location = useLocation()
  const { currentUser } = useCurrentUser()
  const { values, handleChange } = useFormikContext<OfferTypeFormValues>()
  const [subcategories, setSubcategories] = useState<
    SubcategoryResponseModel[]
  >([])
  const [venueType, setVenueType] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const queryParams = new URLSearchParams(location.search)
  const queryVenueId = queryParams.get('lieu')
  const queryOffererId = queryParams.get('structure')
  const isCategorySelectionActive = useNewIndividualOfferType()

  useEffect(() => {
    async function loadData() {
      // prevent admin from loading all venues
      const shouldLoadData =
        !currentUser.isAdmin || queryOffererId || queryVenueId

      if (isCategorySelectionActive && shouldLoadData) {
        setIsLoading(true)
        const [queriedVenueType, queriedSubcategories] =
          await getVenueTypeAndSubcategories(queryVenueId, queryOffererId)
        setVenueType(queriedVenueType)
        setSubcategories(queriedSubcategories)
        setIsLoading(false)
      }
    }
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    loadData()
  }, [queryVenueId, isCategorySelectionActive, queryOffererId])

  const venueTypeMostUsedSubcategories =
    venueType && venueTypeSubcategoriesMapping[venueType]

  if (isLoading) {
    return <Spinner />
  }

  return (
    <>
      {isCategorySelectionActive && venueTypeMostUsedSubcategories && (
        <FormLayout.Section
          title="Quelle est la catégorie de l’offre ?"
          description="Ces catégories sont suggérées d’après les catégories les plus fréquemment sélectionnées pour votre type de lieu."
          className={styles['subcategory-section']}
        >
          {venueTypeMostUsedSubcategories.map(
            (subcategory: SubcategoryIdEnum) => (
              <RadioButton
                className={styles['individual-radio-button-subcategory']}
                key={subcategory}
                withBorder
                value={subcategory}
                label={
                  subcategories.find((s) => s.id === subcategory)?.proLabel ||
                  ''
                }
                name="individualOfferSubcategory"
                variant={BaseRadioVariant.SECONDARY}
              />
            )
          )}
          <RadioButton
            className={styles['individual-radio-button-subcategory']}
            withBorder
            value="OTHER"
            label="Autre"
            name="individualOfferSubcategory"
            variant={BaseRadioVariant.SECONDARY}
          />
        </FormLayout.Section>
      )}

      {(!venueTypeMostUsedSubcategories ||
        values.individualOfferSubcategory === 'OTHER') && (
        <FormLayout.Section
          title="Votre offre est :"
          className={styles['subtype-section']}
        >
          <FormLayout.Row inline mdSpaceAfter>
            <RadioButtonWithImage
              className={styles['individual-radio-button']}
              name="individualOfferSubtype"
              icon={thingStrokeIcon}
              isChecked={
                values.individualOfferSubtype ===
                INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD
              }
              label="Un bien physique"
              description="Livre, instrument de musique, abonnement, cartes et pass…"
              onChange={handleChange}
              value={INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD}
              dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_GOOD}`}
            />
          </FormLayout.Row>

          <FormLayout.Row inline mdSpaceAfter>
            <RadioButtonWithImage
              className={styles['individual-radio-button']}
              name="individualOfferSubtype"
              icon={strokeVirtualThingIcon}
              isChecked={
                values.individualOfferSubtype ===
                INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD
              }
              label="Un bien numérique"
              description="Ebook, jeu vidéo, abonnement streaming..."
              onChange={handleChange}
              value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD}
              dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_GOOD}`}
            />
          </FormLayout.Row>

          <FormLayout.Row inline mdSpaceAfter>
            <RadioButtonWithImage
              className={styles['individual-radio-button']}
              name="individualOfferSubtype"
              icon={strokeDateIcon}
              isChecked={
                values.individualOfferSubtype ===
                INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT
              }
              label="Un évènement physique daté"
              description="Concert, représentation, conférence, ateliers..."
              onChange={handleChange}
              value={INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT}
              dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.PHYSICAL_EVENT}`}
            />
          </FormLayout.Row>

          <FormLayout.Row inline mdSpaceAfter>
            <RadioButtonWithImage
              className={styles['individual-radio-button']}
              name="individualOfferSubtype"
              icon={strokeVirtualEventIcon}
              isChecked={
                values.individualOfferSubtype ===
                INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT
              }
              label="Un évènement numérique daté"
              description="Livestream, cours en ligne, conférence en ligne..."
              onChange={handleChange}
              value={INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}
              dataTestid={`radio-${INDIVIDUAL_OFFER_SUBTYPE.VIRTUAL_EVENT}`}
            />
          </FormLayout.Row>
        </FormLayout.Section>
      )}
    </>
  )
}

export default IndividualOfferType
