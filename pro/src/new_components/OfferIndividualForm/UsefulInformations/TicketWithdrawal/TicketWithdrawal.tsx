import { RadioGroup, Select } from 'ui-kit'
import React, { useEffect } from 'react'
import {
  TICKETWITHDRAWAL,
  ticketSentDateOptions,
  ticketWithdrawalHourOptions,
  ticketWithdrawalTypeRadios,
} from './constants'
import { FORM_DEFAULT_VALUES } from 'new_components/OfferIndividualForm'
import FormLayout from 'new_components/FormLayout'
import { IOfferIndividualFormValues } from '../../types'
import { IOfferSubCategory } from 'core/Offers/types'
import styles from './TicketWithdrawal.module.scss'
import { useFormikContext } from 'formik'

export interface ITicketWithdrawalProps {
  subCategories: IOfferSubCategory[]
}

const TicketWithdrawal = ({
  subCategories,
}: ITicketWithdrawalProps): JSX.Element => {
  const {
    values: { subcategoryId, ticketWithdrawal },
    setFieldValue,
  } = useFormikContext<IOfferIndividualFormValues>()

  const subCategory = subCategories.find(s => s.id === subcategoryId)
  const isEvent = subCategory?.isEvent

  useEffect(
    function onSubCategoryChange() {
      if (!isEvent) {
        setFieldValue(
          'ticketWithdrawal',
          FORM_DEFAULT_VALUES['ticketWithdrawal']
        )
        setFieldValue('ticketSentDate', FORM_DEFAULT_VALUES['ticketSentDate'])
        setFieldValue(
          'ticketWithdrawalHour',
          FORM_DEFAULT_VALUES['ticketWithdrawalHour']
        )
      }
    },
    [subcategoryId]
  )

  useEffect(
    function onTicketWithdrawalChange() {
      if (ticketWithdrawal !== TICKETWITHDRAWAL.emailTicket) {
        setFieldValue('ticketSentDate', FORM_DEFAULT_VALUES['ticketSentDate'])
      } else if (ticketWithdrawal !== TICKETWITHDRAWAL.onPlaceTicket) {
        setFieldValue(
          'ticketWithdrawalHour',
          FORM_DEFAULT_VALUES['ticketWithdrawalHour']
        )
      }
    },
    [ticketWithdrawal]
  )

  return (
    <>
      <FormLayout.Row>
        <RadioGroup
          group={ticketWithdrawalTypeRadios}
          legend="Comment les billets, places seront-ils transmis ?"
          name="ticketWithdrawal"
        />
      </FormLayout.Row>

      {ticketWithdrawal === TICKETWITHDRAWAL.emailTicket && (
        <FormLayout.Row>
          <div className={styles['ticket-options']}>
            <Select
              label="Date d’envoi"
              name="ticketSentDate"
              options={ticketSentDateOptions}
            />
            <p>avant le début de l'événement</p>
          </div>
        </FormLayout.Row>
      )}

      {ticketWithdrawal === TICKETWITHDRAWAL.onPlaceTicket && (
        <FormLayout.Row>
          <div className={styles['ticket-options']}>
            <Select
              label="Heure de retrait"
              name="ticketWithdrawalHour"
              options={ticketWithdrawalHourOptions}
            />
            <p>avant le début de l'événement</p>
          </div>
        </FormLayout.Row>
      )}
    </>
  )
}

export default TicketWithdrawal
