import { FormLayout } from 'components/FormLayout/FormLayout'
import { ImageUploaderOffer } from 'components/IndividualOfferForm/ImageUploaderOffer/ImageUploaderOffer'
import { DurationInput } from 'ui-kit/form/DurationInput/DurationInput'
import { Select } from 'ui-kit/form/Select/Select'
import { TextArea } from 'ui-kit/form/TextArea/TextArea'
import { TextInput } from 'ui-kit/form/TextInput/TextInput'
import { InfoBox } from 'ui-kit/InfoBox/InfoBox'
import { DEFAULT_DETAILS_INTITIAL_VALUES } from './constants'

type DetailsScreenProps = {}

export const DetailsForm = ({}: DetailsScreenProps): JSX.Element => {
  const hasAuthor = true
  const hasPerformer = true
  const hasEan = true
  const hasSpeaker = true
  const hasStageDirector = true
  const hasVisa = true
  const hasDurationMinutes = true

  return (
    <>
      <FormLayout.Section title="A propos de votre offre">
        <FormLayout.Row>
          <TextInput
            countCharacters
            label="Titre de l’offre"
            maxLength={90}
            name="name"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <TextArea
            countCharacters
            isOptional
            label="Description"
            maxLength={1000}
            name="description"
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <Select label="Lieu" name="venueId" options={[]} />
        </FormLayout.Row>
      </FormLayout.Section>

      <FormLayout.Section title="Type d’offre">
        <FormLayout.Row
          sideComponent={
            <InfoBox
              link={{
                isExternal: true,
                to: 'https://aide.passculture.app/hc/fr/articles/4411999013265--Acteurs-Culturels-Quelle-cat%C3%A9gorie-et-sous-cat%C3%A9gorie-choisir-lors-de-la-cr%C3%A9ation-d-offres-',
                text: 'Quelles catégories choisir ?',
                target: '_blank',
              }}
              svgAlt="Nouvelle fenêtre"
            >
              Une sélection précise de vos catégories permettra au grand public
              de facilement trouver votre offre. Une fois validées, vous ne
              pourrez pas les modifier.
            </InfoBox>
          }
        >
          <Select
            label="Catégorie"
            name="categoryId"
            options={[]}
            defaultOption={{
              label: 'Choisir une catégorie',
              value: DEFAULT_DETAILS_INTITIAL_VALUES.categoryId,
            }}
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <Select
            label="Sous-catégorie"
            name="subcategoryId"
            options={[]}
            defaultOption={{
              label: 'Choisir une sous-catégorie',
              value: DEFAULT_DETAILS_INTITIAL_VALUES.subcategoryId,
            }}
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <Select
            label="Genre musical"
            name="gtl_id"
            options={[]}
            defaultOption={{
              label: 'Choisir un genre musical',
              value: DEFAULT_DETAILS_INTITIAL_VALUES.gtl_id,
            }}
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <Select
            label="Type de spectacle"
            name="showType"
            options={[]}
            defaultOption={{
              label: 'Choisir un type de spectacle',
              value: DEFAULT_DETAILS_INTITIAL_VALUES.showType,
            }}
          />
        </FormLayout.Row>
        <FormLayout.Row>
          <Select
            label="Sous-type"
            name="showSubType"
            options={[]}
            defaultOption={{
              label: 'Choisir un sous-type',
              value: DEFAULT_DETAILS_INTITIAL_VALUES.showSubType,
            }}
          />
        </FormLayout.Row>
      </FormLayout.Section>
      <ImageUploaderOffer
        onImageUpload={async () => {}}
        onImageDelete={async () => {}}
        imageOffer={{
          originalUrl: '',
          url: '',
          credit: '',
        }}
      />
      <FormLayout.Section title="Informations artistiques">
        {hasSpeaker && (
          <FormLayout.Row>
            <TextInput
              isOptional
              label="Intervenant"
              maxLength={1000}
              name="speaker"
            />
          </FormLayout.Row>
        )}
        {hasAuthor && (
          <FormLayout.Row>
            <TextInput
              isOptional
              label="Auteur"
              maxLength={1000}
              name="author"
            />
          </FormLayout.Row>
        )}
        {hasVisa && (
          <FormLayout.Row>
            <TextInput
              isOptional
              label="Visa d’exploitation"
              maxLength={1000}
              name="visa"
            />
          </FormLayout.Row>
        )}
        {hasStageDirector && (
          <FormLayout.Row>
            <TextInput
              isOptional
              label="Metteur en scène"
              maxLength={1000}
              name="stageDirector"
            />
          </FormLayout.Row>
        )}
        {hasPerformer && (
          <FormLayout.Row>
            <TextInput
              isOptional
              label="Interprète"
              maxLength={1000}
              name="performer"
            />
          </FormLayout.Row>
        )}
        {hasEan && (
          <FormLayout.Row>
            <TextInput
              isOptional
              label="EAN-13 (European Article Numbering)"
              countCharacters
              name="ean"
              maxLength={13}
            />
          </FormLayout.Row>
        )}

        {hasDurationMinutes && (
          <FormLayout.Row>
            <DurationInput isOptional label={'Durée'} name="durationMinutes" />
          </FormLayout.Row>
        )}
      </FormLayout.Section>
    </>
  )
}
