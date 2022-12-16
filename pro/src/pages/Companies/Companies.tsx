import { Form, Formik, FormikProvider, useFormik } from 'formik'
import React, { useEffect, useState } from 'react'

import { api } from 'apiClient/api'
import { GetOffererNameResponseModel } from 'apiClient/v1'
import getOffererAdapter from 'core/Offerers/getOffererAdapter/getOffererAdapter'
import { IOfferer } from 'core/Offerers/types'
import { useNavigate } from 'hooks'
import { Title } from 'ui-kit'
import SelectAutocomplete from 'ui-kit/form/SelectAutoComplete2/SelectAutocomplete'
import Spinner from 'ui-kit/Spinner/Spinner'
import { sortByLabel } from 'utils/strings'

import styles from './Companies.module.scss'
import { Offerer } from './Offerer'
import { Venue } from './Offerer/Venue'

const NB_DISPLAYED_OFFERER = 10

const Companies = (): JSX.Element => {
  const [isReady, setIsReady] = useState<boolean>(false)
  const [nbDisplayedOfferers, setNbDisplayedOfferers] =
    useState<number>(NB_DISPLAYED_OFFERER)
  const [offererNames, setOffererNames] = useState<SelectOptions>([])
  const [offerers, setOfferers] = useState<IOfferer[]>([])
  const [selectedOfferer, setSelectedOfferer] = useState<IOfferer>()
  const navigate = useNavigate()

  useEffect(() => {
    async function fetchOffererNames() {
      try {
        const venueResponse = await api.getVenues()
        console.log('venueResponse', venueResponse)
        const nameResponse = await api.listOfferersNames(
          true, // validated?: boolean | null,
          true, // validatedForUser?: boolean | null,
          null // offererId?: string | null,
        )
        const options = nameResponse.offerersNames
          .sort((a, b) => a.name.localeCompare(b.name, 'fr'))
          .map(item => {
            return {
              value: String(item.id),
              label: item.name,
            }
          })
        setOffererNames(options)

        if (nameResponse.offerersNames.length > 0) {
          const offererResponse = await getOffererAdapter(options[0].value)
          if (offererResponse.isOk) {
            formik.setFieldValue('offererName', offererResponse.payload.id)
            setSelectedOfferer(offererResponse.payload)
            setOfferers([offererResponse.payload])
          }
        }
      } catch {
        navigate('/404')
      }
      setIsReady(true)
    }
    fetchOffererNames()
  }, [])

  const formik = useFormik({
    initialValues: { offererName: selectedOfferer?.id || '' },
    onSubmit: () => {},
  })

  useEffect(() => {
    async function fetchData() {
      const offererResponse = await getOffererAdapter(formik.values.offererName)
      if (offererResponse.isOk) {
        setSelectedOfferer(offererResponse.payload)
        setOfferers([...offerers, offererResponse.payload])
      }
    }
    if (formik.values.offererName) {
      const newSelectedOfferer = offerers.find(
        offerer => offerer.id === formik.values.offererName
      )
      if (newSelectedOfferer) {
        setSelectedOfferer(newSelectedOfferer)
      } else {
        fetchData()
      }
    }
    formik.values.offererName && fetchData()
  }, [offerers, formik.values.offererName])

  return (
    <>
      <Title level={1}>Vos entreprises</Title>

      {!isReady && <Spinner />}
      {isReady && (
        <>
          <FormikProvider value={formik}>
            <Form>
              <SelectAutocomplete
                fieldName="offererName"
                label="Structures"
                options={offererNames}
                hideArrow={true}
                resetOnOpen={false}
              />
            </Form>
          </FormikProvider>

          <div className={styles['offerer-list']}>
            {selectedOfferer?.managedVenues.map(venue => (
              <Venue
                key={venue.id}
                venue={venue}
                className={styles['offerer-list-item']}
              />
            ))}
          </div>
        </>
      )}
    </>
  )
}

export default Companies
