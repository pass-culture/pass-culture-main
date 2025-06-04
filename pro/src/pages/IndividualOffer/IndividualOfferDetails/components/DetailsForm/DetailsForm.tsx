import { useFormContext } from 'react-hook-form'

import { CategoryResponseModel, SubcategoryResponseModel } from 'apiClient/v1'
import { useAnalytics } from 'app/App/analytics/firebase'
import { useIndividualOfferContext } from 'commons/context/IndividualOfferContext/IndividualOfferContext'
import { Events } from 'commons/core/FirebaseEvents/constants'
import { CATEGORY_STATUS } from 'commons/core/Offers/constants'
import { IndividualOfferImage } from 'commons/core/Offers/types'
import { useActiveFeature } from 'commons/hooks/useActiveFeature'
import { UploaderModeEnum } from 'commons/utils/imageUploadTypes'
import { FormLayout } from 'components/FormLayout/FormLayout'
import { MarkdownInfoBox } from 'components/MarkdownInfoBox/MarkdownInfoBox'
import { OnImageUploadArgs } from 'components/ModalImageUpsertOrEdit/ModalImageUpsertOrEdit'
import fullMoreIcon from 'icons/full-more.svg'
import { DEFAULT_DETAILS_FORM_VALUES } from 'pages/IndividualOffer/IndividualOfferDetails/commons/constants'
import { DetailsFormValues } from 'pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { isSubCategoryCD } from 'pages/IndividualOffer/IndividualOfferDetails/commons/utils'
import { Callout } from 'ui-kit/Callout/Callout'
import { CalloutVariant } from 'ui-kit/Callout/types'
import { Select } from 'ui-kit/formV2/Select/Select'
import { TextArea } from 'ui-kit/formV2/TextArea/TextArea'
import { TextInput } from 'ui-kit/formV2/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'

import styles from './DetailsForm.module.scss'
import { DetailsSubForm } from './DetailsSubForm/DetailsSubForm'
import { ImageUploaderOffer } from './ImageUploaderOffer/ImageUploaderOffer'
import { Subcategories } from './Subcategories/Subcategories'

type DetailsFormProps = {
  isEanSearchDisplayed: boolean
  isProductBased: boolean
  venuesOptions: { label: string; value: string }[]
  filteredCategories: CategoryResponseModel[]
  filteredSubcategories: SubcategoryResponseModel[]
  readOnlyFields: string[]
  categoryStatus: CATEGORY_STATUS
  displayedImage?: IndividualOfferImage | OnImageUploadArgs
  onImageUpload: (values: OnImageUploadArgs) => void
  onImageDelete: () => void
}

const classifyWithGPT = async (
  prompt: string
): Promise<{
  subcategory_ID: string
  gtl_id: string
}> => {
  const apiKey = import.meta.env.VITE_OPENAI_API_KEY
  const apiUrl =
    import.meta.env.VITE_OPENAI_API_BASE_URL ||
    'https://api.openai.com/v1/chat/completions'

  if (!apiKey) {
    throw new Error('OPENAI_API_KEY manquante')
  }

  const body = {
    model: 'gpt-4.1',
    messages: [{ role: 'user', content: prompt }],
    temperature: 0,
  }

  const res = await fetch(apiUrl, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify(body),
  })

  if (!res.ok) {
    throw new Error(`Erreur OpenAI: ${res.status} ${res.statusText}`)
  }

  const data = await res.json()
  const content = data.choices?.[0]?.message?.content
  if (!content) {
    throw new Error('Réponse vide de ChatGPT')
  }

  // Extraction JSON robuste
  let json
  try {
    const match = content.match(/\{[\s\S]*\}/)
    json = match ? JSON.parse(match[0]) : JSON.parse(content)
  } catch {
    throw new Error('Impossible de parser la réponse JSON de ChatGPT')
  }
  return json
}

const getChatGPTPrompt = (title: string, description: string) => `
"Tu es un expert en classification d'offres. Tu es capable de deviner la catégorie et la sous-catégorie d'une offre en fonction de son titre et de sa description.

Voici les catégories et sous-catégories disponibles :
(Catégorie ; category_ID ; Sous-catégorie ; subcategory_ID ; Définition)
(Beaux-arts ; BEAUX_ARTS ; Matériel arts créatifs ; MATERIEL_ART_CREATIF ; Fournitures utilisées pour les activités de création artistique (peinture, dessin, sculpture, etc.).)(Carte jeunes ; CARTE_JEUNES ; Carte jeunes ; CARTE_JEUNES ; Carte offrant des réductions ou avantages culturels aux jeunes (cinéma, concerts, musées, etc.).)(Cinéma ; CINEMA ; Carte cinéma illimité ; CARTE_CINE_ILLIMITE ; Abonnement permettant un accès illimité aux séances de cinéma dans un réseau spécifique.)(Cinéma ; CINEMA ; Carte cinéma multi-séances ; CARTE_CINE_MULTISEANCES ; Carte prépayée pour un nombre déterminé de séances, avec un retrait physique au guichet du cinéma)(Films, vidéos ; FILM ; Abonnement médiathèque ; ABO_MEDIATHEQUE ; Accès régulier à une médiathèque incluant films, vidéos, supports culturels.)(Films, vidéos ; FILM ; Support physique (DVD, Blu-ray...) ; SUPPORT_PHYSIQUE_FILM ; Achat de films ou vidéos sur support matériel.)(Instrument de musique ; INSTRUMENT ; Achat instrument ; ACHAT_INSTRUMENT ; Acquisition d'un instrument de musique (neuf ou occasion).)(Instrument de musique ; INSTRUMENT ; Location instrument ; LOCATION_INSTRUMENT ; Mise à disposition temporaire d'un instrument moyennant un loyer.)(Instrument de musique ; INSTRUMENT ; Partition ; PARTITION ; Achat de partitions papier ou numériques pour jouer de la musique.)(Jeux ; JEU ; Escape game ; ESCAPE_GAME ; Jeu d'évasion grandeur nature basé sur la résolution d'énigmes.)(Livre ; LIVRE ; Abonnement (bibliothèques, médiathèques...) ; ABO_BIBLIOTHEQUE ; Accès régulier à des livres via une structure culturelle.)(Livre ; LIVRE ; Livre papier ; LIVRE_PAPIER ; Livre imprimé traditionnel.)(Livre ; LIVRE ; Livre audio sur support physique ; LIVRE_AUDIO_PHYSIQUE ; Livre lu enregistré sur CD ou autre support tangible.)(Musée, patrimoine, architecture, arts visuels ; MUSEE ; Abonnement musée, carte ou pass ; CARTE_MUSEE ; Entrée libre ou réduite à des musées via une carte annuelle.)(Musique enregistrée ; MUSIQUE_ENREGISTREE ; CD ; SUPPORT_PHYSIQUE_MUSIQUE_CD ; Support optique contenant de la musique.)(Musique enregistrée ; MUSIQUE_ENREGISTREE ; Vinyles et autres supports ; SUPPORT_PHYSIQUE_MUSIQUE_VINYLE ; Supports analogiques ou alternatifs au CD (vinyle, cassette…).)(Musique live ; MUSIQUE_LIVE ; Abonnement concert ; ABO_CONCERT ; Pass ou abonnement pour assister à des concerts en illimité ou à tarif réduit.)(Pratique artistique ; PRATIQUE_ART ; Abonnement pratique artistique ; ABO_PRATIQUE_ART ; Accès régulier à des cours ou ateliers de création artistique.)(Spectacle vivant ; SPECTACLE ; Abonnement spectacle ; ABO_SPECTACLE ; Carte ou forfait donnant accès à plusieurs spectacles. Donc un spectacle en particulier ne peut pas être dans cette sous-catégorie (ce sera alors plutôt un livre car le texte de la pièce).)

Avec le titre et la description d'une offre, que je vais t'envoyer, tu dois retourner un objet JSON composé uniquement de subcategory_ID et gtl_id. Voici le schéma de l'objet JSON à respecter impérativement :

{
  "subcategory_ID": "...",
  "gtl_id": "..."
}

À noter que le domaine d'activité est le domaine de la culture et des offres culturelles au sens large. Tu utiliseras donc tes connaissances dans les offres culturelles, ainsi que des recherches web, pour trouver systématiquement la bonne sous-catégorie. Il ne t'est pas possible de ne pas proposer de sous-catégorie. Mais tu ne dois pas te tromper ! Assure-toi bien de faire les recherches nécessaires pour ne pas choisir n'importe quoi.

Pour les sous-catégories SUPPORT_PHYSIQUE_MUSIQUE_CD;SUPPORT_PHYSIQUE_MUSIQUE_VINYLE;ABO_CONCERT, tu dois aussi choisir obligatoirement un ""genre musical"" en renvoyant, en plus de la subcategory, un gtl_id, parmi ceux-ci : (Libellé;gtl_id);(Musique Classique;01000000);(Jazz / Blues;02000000);(Bandes originales;03000000);(Electro;04000000);(Pop;05000000);(Rock;06000000);(Metal;07000000);(Alternatif;08000000);(Variétés;09000000);(Funk / Soul / RnB / Disco;10000000);(Rap / Hip Hop;11000000);(Reggae / Ragga;12000000);(Musique du monde;13000000);(Country / Folk;14000000);(Vidéos musicales;15000000);(Compilations;16000000);(Ambiance;17000000);(Enfants;18000000);(Autre;19000000)Voici l'offre concernée :

TITRE = "${title}"
DESCRIPTION = "${description}"
`

export const DetailsForm = ({
  isEanSearchDisplayed,
  isProductBased,
  venuesOptions,
  filteredCategories,
  filteredSubcategories,
  readOnlyFields,
  categoryStatus,
  displayedImage,
  onImageUpload,
  onImageDelete,
}: DetailsFormProps): JSX.Element => {
  const { logEvent } = useAnalytics()
  const {
    register,
    watch,
    getValues,
    setValue,
    resetField,
    setError,
    clearErrors,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  const isAutomaticallyAssignOfferCategory = useActiveFeature(
    'WIP_HACKATON_AUTOMATICALLY_ASSIGN_OFFER_CATEGORY'
  )

  const subcategoryId = watch('subcategoryId')
  const { offer } = useIndividualOfferContext()

  const isSubCategorySelected =
    subcategoryId !== DEFAULT_DETAILS_FORM_VALUES.subcategoryId

  const showAddVenueBanner = venuesOptions.length === 0

  const logOnImageDropOrSelected = () => {
    logEvent(Events.DRAG_OR_SELECTED_IMAGE, {
      imageType: UploaderModeEnum.OFFER,
      imageCreationStage: 'add image',
    })
  }

  const { categories, subCategories } = useIndividualOfferContext()

  const onAICategorizeBlur = async () => {
    const { name, description } = getValues()
    console.log('name', name)
    console.log('description', description)

    if (!name || !description) {
      return
    }

    try {
      setError('root', { type: 'asyncJobNotFinished' })
      resetField('categoryId', { keepTouched: true })
      resetField('subcategoryId', { keepTouched: true })
      resetField('gtl_id', { keepTouched: true })

      const prompt = getChatGPTPrompt(name, description)
      const res = await classifyWithGPT(prompt)

      const subcategory = subCategories.find(
        (subcat) => subcat.id === res.subcategory_ID
      ) as SubcategoryResponseModel
      const category = categories.find(
        (cat) => cat.id === subcategory!.categoryId
      ) as CategoryResponseModel

      console.log('subcategory', subcategory)
      console.log('category', category)

      console.group('API Call')
      console.log('res', res)
      console.log('subcategoryId', res.subcategory_ID)
      console.log('categoryId', category.id)
      console.log('gtl_id', res.gtl_id)
      console.groupEnd()

      setValue('subcategoryId', res.subcategory_ID)
      setValue('categoryId', category.id)
      if (res.gtl_id) {
        setValue('gtl_id', res.gtl_id)
      }

      watch(['categoryId', 'gtl_id'])
    } catch (err) {
      console.error('Prediction failed', err)
    } finally {
      clearErrors('root')
    }
  }

  return (
    <>
      <FormLayout.Section title="À propos de votre offre">
        {showAddVenueBanner && (
          <FormLayout.Row className={styles['row']}>
            <Callout
              links={[
                {
                  href: `/parcours-inscription/structure`,
                  icon: {
                    src: fullMoreIcon,
                    alt: '',
                  },
                  label: 'Ajouter une structure',
                },
              ]}
              variant={CalloutVariant.ERROR}
            >
              Pour créer une offre, vous devez d’abord créer une structure.
            </Callout>
          </FormLayout.Row>
        )}
        {!showAddVenueBanner && (
          <>
            {venuesOptions.length > 1 && (
              <FormLayout.Row className={styles['row']}>
                <Select
                  label="Qui propose l’offre ?"
                  options={venuesOptions}
                  defaultOption={{
                    value: '',
                    label: 'Sélectionner la structure',
                  }}
                  {...register('venueId')}
                  onChange={(e) => {
                    if (isProductBased) {
                      return
                    }

                    setValue('venueId', e.target.value)
                  }}
                  disabled={
                    readOnlyFields.includes('venueId') ||
                    venuesOptions.length === 1
                  }
                  error={errors.venueId?.message}
                />
              </FormLayout.Row>
            )}
            <FormLayout.Row className={styles['row']}>
              <TextInput
                count={watch('name').length}
                label="Titre de l’offre"
                maxLength={90}
                {...register('name')}
                error={errors.name?.message}
                required
                disabled={readOnlyFields.includes('name')}
                onBlur={
                  isAutomaticallyAssignOfferCategory
                    ? onAICategorizeBlur
                    : undefined
                }
              />
            </FormLayout.Row>
            <FormLayout.Row
              sideComponent={<MarkdownInfoBox />}
              className={styles['row']}
            >
              <TextArea
                label="Description"
                maxLength={10000}
                {...register('description')}
                disabled={readOnlyFields.includes('description')}
                required={isAutomaticallyAssignOfferCategory}
                error={errors.description?.message}
                onBlur={
                  isAutomaticallyAssignOfferCategory
                    ? onAICategorizeBlur
                    : undefined
                }
              />
            </FormLayout.Row>
            {(categoryStatus === CATEGORY_STATUS.ONLINE ||
              offer?.isDigital) && (
              <FormLayout.Row
                sideComponent={
                  <InfoBox>
                    Lien vers lequel seront renvoyés les bénéficiaires ayant
                    réservé votre offre sur l’application pass Culture.
                  </InfoBox>
                }
                className={styles['row']}
              >
                <TextInput
                  label="URL d’accès à l’offre"
                  type="text"
                  description="Format : https://exemple.com"
                  disabled={readOnlyFields.includes('url')}
                  {...register('url')}
                  error={errors.url?.message}
                  required
                />
              </FormLayout.Row>
            )}
          </>
        )}
      </FormLayout.Section>
      <ImageUploaderOffer
        displayedImage={displayedImage}
        onImageUpload={onImageUpload}
        onImageDelete={onImageDelete}
        onImageDropOrSelected={logOnImageDropOrSelected}
        hideActionButtons={isProductBased}
      />
      <div
        style={isAutomaticallyAssignOfferCategory ? { display: 'none' } : {}}
      >
        {!showAddVenueBanner && (
          <Subcategories
            readOnlyFields={readOnlyFields}
            filteredCategories={filteredCategories}
            filteredSubcategories={filteredSubcategories}
          />
        )}
        {isSubCategorySelected && (
          <DetailsSubForm
            isEanSearchDisplayed={isEanSearchDisplayed}
            isProductBased={isProductBased}
            isOfferCD={isSubCategoryCD(subcategoryId)}
            readOnlyFields={readOnlyFields}
          />
        )}
      </div>
    </>
  )
}
