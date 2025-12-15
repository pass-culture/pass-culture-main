import { screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { FormProvider, useForm } from 'react-hook-form'

import { SubcategoryIdEnum, WithdrawalTypeEnum } from '@/apiClient/v1'
import { IndividualOfferContext } from '@/commons/context/IndividualOfferContext/IndividualOfferContext'
import {
  getIndividualOfferFactory,
  individualOfferContextValuesFactory,
  subcategoryFactory,
} from '@/commons/utils/factories/individualApiFactories'
import { sharedCurrentUserFactory } from '@/commons/utils/factories/storeFactories'
import { renderWithProviders } from '@/commons/utils/renderWithProviders'
import { MOCKED_SUBCATEGORY } from '@/pages/IndividualOffer/commons/__mocks__/constants'

import type { IndividualOfferPracticalInfosFormValues } from '../../commons/types'
import {
  IndividualOfferPracticalInfosForm,
  type IndividualOfferPracticalInfosFormProps,
} from './IndividualOfferPracticalInfosForm'

function renderIndividualOfferPracticalInfosForm(
  props?: Partial<IndividualOfferPracticalInfosFormProps>
) {
  function IndividualOfferPracticalInfosFormWrapper() {
    const form = useForm<IndividualOfferPracticalInfosFormValues>({
      defaultValues: {
        withdrawalType: WithdrawalTypeEnum.BY_EMAIL,
      },
    })
    return (
      <IndividualOfferContext.Provider
        value={individualOfferContextValuesFactory({
          categories: [],
          subCategories: [],
        })}
      >
        <FormProvider {...form}>
          <IndividualOfferPracticalInfosForm
            offer={getIndividualOfferFactory()}
            stocks={[]}
            subCategory={MOCKED_SUBCATEGORY.WIDTHDRAWABLE_OFFLINE}
            {...props}
          />
        </FormProvider>
      </IndividualOfferContext.Provider>
    )
  }
  renderWithProviders(<IndividualOfferPracticalInfosFormWrapper />, {
    user: sharedCurrentUserFactory(),
  })
}

describe('IndividualOfferPracticalInfosForm', () => {
  it('should show the warning booking callout if the offer is not an event', () => {
    renderIndividualOfferPracticalInfosForm({
      offer: getIndividualOfferFactory({ isEvent: false }),
    })

    expect(
      screen.getByText(/La validation de la contremarque est obligatoire/)
    ).toBeInTheDocument()
  })

  it('should show the withdrawal block if the sub category is withdrawable', () => {
    renderIndividualOfferPracticalInfosForm({
      offer: getIndividualOfferFactory({
        subcategoryId: SubcategoryIdEnum.FESTIVAL_CINE,
      }),
    })

    expect(
      screen.getByRole('group', {
        name: /Précisez la façon dont vous distribuerez les billets/,
      })
    ).toBeInTheDocument()
  })

  it('should show a warning callout if the offer is physical and offline', () => {
    renderIndividualOfferPracticalInfosForm({
      offer: getIndividualOfferFactory({
        subcategoryId: SubcategoryIdEnum.FESTIVAL_CINE,
        isEvent: false,
      }),
    })

    expect(
      screen.getByText(/La livraison d’article est interdite/)
    ).toBeInTheDocument()
  })

  it('should show the notification email field if the notification checkbox is checked', async () => {
    renderIndividualOfferPracticalInfosForm()

    const notificationCheckbox = screen.getByRole('checkbox', {
      name: 'Être notifié par email des réservations',
    })

    expect(notificationCheckbox).not.toBeChecked()

    expect(
      screen.queryByLabelText('Email auquel envoyer les notifications')
    ).not.toBeInTheDocument()
    expect(screen.queryByText('Obligatoire')).not.toBeInTheDocument()

    await userEvent.click(notificationCheckbox)

    expect(
      screen.getByLabelText(/Email auquel envoyer les notifications/)
    ).toBeInTheDocument()
    expect(screen.getByText('Obligatoire')).toBeInTheDocument()
  })

  it('should show a warning callout with a 10 days expiration if the offer is a physical book', () => {
    renderIndividualOfferPracticalInfosForm({
      offer: getIndividualOfferFactory({
        subcategoryId: SubcategoryIdEnum.LIVRE_PAPIER,
        isEvent: false,
      }),
      subCategory: subcategoryFactory({ id: SubcategoryIdEnum.LIVRE_PAPIER }),
    })

    expect(
      screen.getByText(
        /la réservation sera automatiquement annulée et remise en vente au bout de 10 jours/
      )
    ).toBeInTheDocument()
  })
})
