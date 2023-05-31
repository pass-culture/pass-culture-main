import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import type { Hit } from 'react-instantsearch-core'

import {
  AdageHeaderLink,
  EducationalInstitutionWithBudgetResponseModel,
} from 'apiClient/adage'
import { apiAdage } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { getEducationalInstitutionWithBudgetAdapter } from 'pages/AdageIframe/app/adapters/getEducationalInstitutionWithBudgetAdapter'
import { defaultAlgoliaHits } from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { ResultType } from 'utils/types'

import { AdageHeaderComponent } from '../AdageHeader'

interface HeaderLinkProps {
  headerLinkLabel: string
  headerLinkName: AdageHeaderLink
}

const renderAdageHeader = (hits: Hit<ResultType>[] = []) => {
  renderWithProviders(<AdageHeaderComponent hits={hits} />)
}

jest.mock('apiClient/api', () => ({
  apiAdage: {
    logHeaderLinkClick: jest.fn(),
  },
}))

describe('AdageHeader', () => {
  const notifyError = jest.fn()

  beforeEach(() => {
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useNotification'),
      error: notifyError,
    }))
  })

  it('should render adage header', () => {
    renderAdageHeader()

    expect(screen.getByRole('link', { name: 'Rechercher' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Pour mon établissement 0' })
    ).toBeInTheDocument()
    expect(screen.getByText('Suivi')).toBeInTheDocument()
  })

  it('should render the number of hits', () => {
    renderAdageHeader([defaultAlgoliaHits, defaultAlgoliaHits])

    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('should display the institution budget', async () => {
    jest
      .spyOn(apiAdage, 'getEducationalInstitutionWithBudget')
      .mockResolvedValueOnce({
        budget: 10000,
      } as EducationalInstitutionWithBudgetResponseModel)

    renderAdageHeader()

    await waitFor(
      async () => await getEducationalInstitutionWithBudgetAdapter()
    )

    expect(screen.getByText('Budget restant')).toBeInTheDocument()
    expect(screen.getByText('10,000€')).toBeInTheDocument()
  })

  it('should return an error when the institution budget could not be retrieved', async () => {
    jest
      .spyOn(apiAdage, 'getEducationalInstitutionWithBudget')
      .mockRejectedValueOnce('')

    renderAdageHeader()

    const response = await getEducationalInstitutionWithBudgetAdapter()

    expect(response.isOk).toBeFalsy()

    expect(notifyError).toHaveBeenNthCalledWith(
      1,
      'Nous avons rencontré un problème lors du chargemement des données'
    )
  })

  const headerLinks: HeaderLinkProps[] = [
    { headerLinkLabel: 'Rechercher', headerLinkName: AdageHeaderLink.SEARCH },
    {
      headerLinkLabel: 'Pour mon établissement 0',
      headerLinkName: AdageHeaderLink.MY_INSTITUTION_OFFERS,
    },
    { headerLinkLabel: 'Suivi', headerLinkName: AdageHeaderLink.ADAGE_LINK },
  ]
  it.each(headerLinks)(
    'should log click on header link',
    async (headerLink: HeaderLinkProps) => {
      renderAdageHeader()

      await userEvent.click(
        screen.getByRole('link', { name: headerLink.headerLinkLabel })
      )
      expect(apiAdage.logHeaderLinkClick).toHaveBeenCalledTimes(1)
      expect(apiAdage.logHeaderLinkClick).toHaveBeenCalledWith({
        header_link_name: headerLink.headerLinkName,
      })
    }
  )
})
