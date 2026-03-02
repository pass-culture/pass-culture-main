import { useFieldArray, useFormContext } from 'react-hook-form'

import { api } from '@/apiClient/api'
import { type ArtistResponseModel, ArtistType } from '@/apiClient/v1'
import { assertOrFrontendError } from '@/commons/errors/assertOrFrontendError'
import { resizeImageURL } from '@/commons/utils/resizeImageURL'
import { Button } from '@/design-system/Button/Button'
import { ButtonColor, ButtonVariant } from '@/design-system/Button/types'
import fullMoreIcon from '@/icons/full-more.svg'
import fullTrashIcon from '@/icons/full-trash.svg'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDescription/commons/types'
import { ApiSelect } from '@/ui-kit/form/ApiSelect/ApiSelect'

import styles from './ArtistField.module.scss'
import avatarPlaceholder from './assets/avatar_placeholder.png'

const ARTIST_TYPE_LABELS: Record<ArtistType, string> = {
  [ArtistType.AUTHOR]: 'Auteur',
  [ArtistType.FILM_ACTOR]: 'Acteur',
  [ArtistType.FILM_DIRECTOR]: 'Réalisateur',
  [ArtistType.PERFORMER]: 'Interprète',
  [ArtistType.STAGE_DIRECTOR]: 'Metteur en scène',
}

const ARTIST_THUMB_WIDTH = 36

type ArtistOption = ArtistResponseModel & { value: string; label: string }

type ArtistFieldProps = {
  readOnly: boolean
  artistType: ArtistType
}

export function ArtistField({
  readOnly,
  artistType,
}: Readonly<ArtistFieldProps>) {
  const {
    control,
    register,
    setValue,
    watch,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  const { fields, append, remove, update } = useFieldArray({
    control,
    name: 'artistOfferLinks',
  })

  const fieldsForType = fields
    .map((field, index) => ({ field, index }))
    .filter(({ field }) => field.artistType === artistType)

  const removeEntry = (indexToRemove: number) => {
    assertOrFrontendError(
      fieldsForType.length > 1,
      '`removeEntry` should not be called when there is only one entry of this type.'
    )

    remove(indexToRemove)
  }

  const resetEntry = (indexToReset: number) => {
    const initialEntry = {
      artistId: null,
      artistName: '',
      artistType,
    }

    update(indexToReset, initialEntry)
  }

  const trashAction = (indexToRemove: number) => {
    // If there is only one entry left for this type, we reset it instead of removing it
    if (fieldsForType.length === 1) {
      resetEntry(indexToRemove)

      return
    }

    removeEntry(indexToRemove)
  }

  return (
    <>
      {fieldsForType.map(({ field, index }) => {
        const { ref } = register(`artistOfferLinks.${index}.artistName`)
        const name = `artistOfferLinks.${index}`
        const artistName = watch(`artistOfferLinks.${index}.artistName`)
        const isTrashDisabled =
          fieldsForType.length === 1 && !artistName?.trim()

        return (
          <div key={field.id} className={styles.row}>
            <div className={styles.select}>
              <ApiSelect<ArtistOption>
                name={name}
                label={ARTIST_TYPE_LABELS[artistType]}
                onSelect={(artist: ArtistOption | undefined) => {
                  if (artist) {
                    setValue(
                      `artistOfferLinks.${index}`,
                      {
                        artistId: artist.id,
                        artistName: artist.name,
                        artistType,
                      },
                      { shouldValidate: true }
                    )
                  }
                }}
                onSearch={(searchText) => {
                  setValue(
                    `artistOfferLinks.${index}`,
                    {
                      artistId: null,
                      artistName: searchText,
                      artistType,
                    },
                    { shouldValidate: true }
                  )
                }}
                searchApi={async (searchText) => {
                  const artists = await api.getArtists(searchText)

                  return artists.map((artist) => ({
                    ...artist,
                    value: artist.id,
                    label: artist.name,
                    thumbUrl: artist.thumbUrl
                      ? resizeImageURL({
                          imageURL: artist.thumbUrl,
                          width: ARTIST_THUMB_WIDTH,
                        })
                      : null,
                  }))
                }}
                error={errors?.artistOfferLinks?.[index]?.artistName?.message}
                minSearchLength={2}
                disabled={readOnly}
                required={false}
                thumbPlaceholder={avatarPlaceholder}
                ref={ref}
              />
            </div>

            {!readOnly && (
              <div className={styles['button-action']}>
                <Button
                  variant={ButtonVariant.SECONDARY}
                  color={ButtonColor.NEUTRAL}
                  icon={fullTrashIcon}
                  iconAlt={
                    fieldsForType.length > 1
                      ? 'Supprimer ce champ'
                      : 'Réinitialiser les valeurs de ce champ'
                  }
                  onClick={() => trashAction(index)}
                  disabled={isTrashDisabled}
                  tooltip={
                    fieldsForType.length > 1
                      ? 'Supprimer ce champ'
                      : 'Réinitialiser les valeurs de ce champ'
                  }
                />
              </div>
            )}
          </div>
        )
      })}
      {!readOnly && (
        <Button
          variant={ButtonVariant.TERTIARY}
          icon={fullMoreIcon}
          color={ButtonColor.NEUTRAL}
          label={`Ajouter un ${ARTIST_TYPE_LABELS[artistType].toLowerCase()}`}
          onClick={() =>
            append(
              { artistId: null, artistName: '', artistType },
              { shouldFocus: true }
            )
          }
        />
      )}
    </>
  )
}
