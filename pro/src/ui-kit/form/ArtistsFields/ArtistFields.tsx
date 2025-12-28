import { useFieldArray, useFormContext } from 'react-hook-form'

import fullMoreIcon from '@/icons/full-more.svg'
import type { DetailsFormValues } from '@/pages/IndividualOffer/IndividualOfferDetails/commons/types'
import { Button } from '@/ui-kit/Button/Button'
import { ButtonVariant } from '@/ui-kit/Button/types'

import { ArtistSelect } from './components/ArtistSelect'

type ArtistFieldsProps = {
  readOnly: boolean
}

export function ArtistFields({ readOnly }: ArtistFieldsProps) {
  const {
    control,
    register,
    watch,
    formState: { errors },
  } = useFormContext<DetailsFormValues>()

  const { fields, append } = useFieldArray({
    control,
    name: 'author',
  })

  return (
    <>
      {fields.map((field, index) => (
        <div key={field.id}>
          <ArtistSelect
            label={'Auteur'}
            disabled={readOnly}
            {...register(`author.${index}`)}
            error={errors.author?.message}
            value={watch(`author.${index}`)?.name}
          />
        </div>
      ))}

      {!readOnly && (
        <Button
          variant={ButtonVariant.TERNARY}
          icon={fullMoreIcon}
          onClick={() =>
            append({ artistId: '', name: '' }, { shouldFocus: true })
          }
        >
          Ajouter un auteur
        </Button>
      )}
    </>
  )
}
