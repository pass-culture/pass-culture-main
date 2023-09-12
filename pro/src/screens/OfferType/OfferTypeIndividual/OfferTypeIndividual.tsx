import { useFormikContext } from 'formik'
import React, { useEffect, useState } from 'react'
import { useLocation } from 'react-router-dom'

import { SubcategoryIdEnum } from 'apiClient/v1'
import FormLayout from 'components/FormLayout'
import { getCategoriesAdapter } from 'core/Offers/adapters'
import { INDIVIDUAL_OFFER_SUBTYPE } from 'core/Offers/constants'
import { OfferSubCategory } from 'core/Offers/types'
import { getVenueAdapter } from 'core/Venue/adapters/getVenueAdapter'
import { Venue } from 'core/Venue/types'
import useNewIndividualOfferType from 'hooks/useNewIndividualOfferType'
import strokeDateIcon from 'icons/stroke-date.svg'
import thingStrokeIcon from 'icons/stroke-thing.svg'
import strokeVirtualEventIcon from 'icons/stroke-virtual-event.svg'
import strokeVirtualThingIcon from 'icons/stroke-virtual-thing.svg'
import { RadioButton } from 'ui-kit'
import { BaseRadioVariant } from 'ui-kit/form/shared/BaseRadio/types'
import RadioButtonWithImage from 'ui-kit/RadioButtonWithImage'

import styles from '../OfferType.module.scss'
import { OfferTypeFormValues } from '../types'

import { venueTypeSubcategoriesMapping } from './venueTypeSubcategoriesMapping'

const OfferTypeIndividual = (): JSX.Element | null => {
  const location = useLocation()
  const { values, handleChange } = useFormikContext<OfferTypeFormValues>()
  const [subcategories, setSubcategories] = useState<OfferSubCategory[]>([])
  const [venue, setVenue] = useState<Venue | null>(null)
  const queryParams = new URLSearchParams(location.search)
  const queryVenueId = queryParams.get('lieu')
  const isCategorySelectionActive = useNewIndividualOfferType()

  useEffect(() => {
    async function loadData() {
      if (Boolean(queryVenueId) && isCategorySelectionActive) {
        const categoriesResponse = await getCategoriesAdapter()
        const venueResponse = await getVenueAdapter(Number(queryVenueId))

        if (categoriesResponse.isOk && venueResponse.isOk) {
          const categoriesData = categoriesResponse.payload
          const { subCategories } = categoriesData
          setSubcategories(subCategories)

          const venueData = venueResponse.payload
          setVenue(venueData)
        }
      }
    }
    loadData()
  }, [queryVenueId])

  const venueType = venue?.venueType
  const venueTypeMostUsedSubcategories =
    venueType && venueTypeSubcategoriesMapping[venueType]

  return (
    <>
      {isCategorySelectionActive && venueTypeMostUsedSubcategories && (
        <FormLayout.Section
          title="Quelle est la catégorie de l’offre ?"
          description="Ces catégories sont suggérées d’après les catégories les plus fréquemment sélectionnées pour votre type de lieu."
          className={styles['subcategory-section']}
        >
          <FormLayout.Row
            inline
            mdSpaceAfter
            className={styles['individual-radio-button-subcategory-group']}
          >
            {venueTypeMostUsedSubcategories.map(
              (subcategory: SubcategoryIdEnum) => (
                <RadioButton
                  className={styles['individual-radio-button-subcategory']}
                  key={subcategory}
                  withBorder
                  value={subcategory}
                  label={
                    subcategories.find(s => s.id === subcategory)?.proLabel ||
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
          </FormLayout.Row>
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

export default OfferTypeIndividual
