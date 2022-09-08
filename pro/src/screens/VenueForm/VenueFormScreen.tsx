import { FormikProvider, useFormik } from 'formik'
import React, { useMemo, useState } from 'react'

import { IOfferer } from 'core/Offerers/types'
import {
  VenueForm,
  validationSchema,
  IVenueFormValues,
} from 'new_components/VenueForm'
import { generateSiretValidationSchema } from 'new_components/VenueForm/Informations/SiretOrCommentFields'
import { Title } from 'ui-kit'

import { IProviders, IVenue, IVenueProviderApi } from '../../core/Venue/types'

import style from './VenueFormScreen.module.scss'

interface IVenueEditionProps {
  isCreatingVenue: boolean
  initialValues: IVenueFormValues
  offerer: IOfferer
  venueTypes: SelectOption[]
  venueLabels: SelectOption[]
  providers?: IProviders[]
  venueProviders?: IVenueProviderApi[]
  venue?: IVenue
}

const VenueFormScreen = ({
  isCreatingVenue,
  initialValues,
  offerer,
  venueTypes,
  venueLabels,
  venueProviders,
  venue,
  providers,
}: IVenueEditionProps): JSX.Element => {
  const onSubmit = () => {
    alert('todo submit form !')
  }

  const [isSiretValued, setIsSiretValued] = useState(true)

  const generateSiretOrCommentValidationSchema: any = useMemo(
    () => generateSiretValidationSchema(offerer.siren, isSiretValued),
    [offerer.siren, isSiretValued]
  )

  const formValidationSchema = validationSchema.concat(
    generateSiretOrCommentValidationSchema
  )

  const formik = useFormik({
    initialValues,
    onSubmit: onSubmit,
    validationSchema: formValidationSchema,
  })

  return (
    <div>
      <Title level={1} className={style['venue-form-heading']}>
        {isCreatingVenue ? 'Création d’un lieu' : 'Lieu'}
      </Title>
      {!isCreatingVenue && (
        <Title level={2} className={style['venue-form-heading']}>
          {initialValues.publicName || initialValues.name}
        </Title>
      )}

      <FormikProvider value={formik}>
        <form onSubmit={formik.handleSubmit}>
          <VenueForm
            isCreatingVenue={isCreatingVenue}
            updateIsSiretValued={setIsSiretValued}
            venueTypes={venueTypes}
            venueLabels={venueLabels}
            venueProvider={venueProviders}
            provider={providers}
            venue={venue}
          />
        </form>
      </FormikProvider>
    </div>
  )
}

export default VenueFormScreen
