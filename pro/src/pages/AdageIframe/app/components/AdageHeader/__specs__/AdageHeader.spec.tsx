import { screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import React from 'react'
import type { Hit } from 'react-instantsearch-core'

import { AdageFrontRoles, AuthenticatedResponse } from 'apiClient/adage'
import { AdageHeaderLink } from 'apiClient/adage/models/AdageHeaderLink'
import { apiAdage } from 'apiClient/api'
import * as useNotification from 'hooks/useNotification'
import { AdageUserContext } from 'pages/AdageIframe/app/providers/AdageUserContext'
import {
  defaultAlgoliaHits,
  defaultEducationalInstitution,
} from 'utils/adageFactories'
import { renderWithProviders } from 'utils/renderWithProviders'
import { ResultType } from 'utils/types'

import { AdageHeaderComponent } from '../AdageHeader'

interface HeaderLinkProps {
  headerLinkLabel: string
  headerLinkName: AdageHeaderLink
}

const renderAdageHeader = (
  hits: Hit<ResultType>[] = [],
  user: AuthenticatedResponse
) => {
  renderWithProviders(
    <AdageUserContext.Provider value={{ adageUser: user }}>
      <AdageHeaderComponent hits={hits} />
    </AdageUserContext.Provider>
  )
}

jest.mock('apiClient/api', () => ({
  apiAdage: {
    logHeaderLinkClick: jest.fn(),
    getEducationalInstitutionWithBudget: jest.fn(),
  },
}))

describe('AdageHeader', () => {
  const notifyError = jest.fn()
  const user = {
    role: AdageFrontRoles.REDACTOR,
    uai: 'uai',
    departmentCode: '30',
    institutionName: 'COLLEGE BELLEVUE',
    institutionCity: 'ALES',
  }

  beforeEach(() => {
    jest.spyOn(useNotification, 'default').mockImplementation(() => ({
      ...jest.requireActual('hooks/useNotification'),
      error: notifyError,
    }))
    jest
      .spyOn(apiAdage, 'getEducationalInstitutionWithBudget')
      .mockResolvedValue(defaultEducationalInstitution)
  })

  it('should render adage header', async () => {
    renderAdageHeader([], user)
    await waitFor(() =>
      expect(
        apiAdage.getEducationalInstitutionWithBudget
      ).toHaveBeenCalledTimes(1)
    )

    expect(screen.getByRole('link', { name: 'Rechercher' })).toBeInTheDocument()
    expect(
      screen.getByRole('link', { name: 'Pour mon établissement 0' })
    ).toBeInTheDocument()
    expect(screen.getByText('Suivi')).toBeInTheDocument()
  })

  it('should render the number of hits', async () => {
    renderAdageHeader([defaultAlgoliaHits, defaultAlgoliaHits], user)
    await waitFor(() =>
      expect(screen.getByText('Budget restant')).toBeInTheDocument()
    )
    expect(screen.getByText('2')).toBeInTheDocument()
  })

  it('should display the institution budget', async () => {
    renderAdageHeader([], user)
    await waitFor(() =>
      expect(screen.getByText('Budget restant')).toBeInTheDocument()
    )

    expect(screen.getByText('1,000€')).toBeInTheDocument()
  })

  it('should return an error when the institution budget could not be retrieved', async () => {
    jest
      .spyOn(apiAdage, 'getEducationalInstitutionWithBudget')
      .mockRejectedValueOnce({})

    renderAdageHeader([], user)
    await waitFor(() =>
      expect(apiAdage.getEducationalInstitutionWithBudget).toHaveBeenCalled()
    )

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
      renderAdageHeader([], user)
      await waitFor(() =>
        expect(screen.getByText('Budget restant')).toBeInTheDocument()
      )

      await userEvent.click(
        screen.getByRole('link', { name: headerLink.headerLinkLabel })
      )
      expect(apiAdage.logHeaderLinkClick).toHaveBeenCalledTimes(1)
      expect(apiAdage.logHeaderLinkClick).toHaveBeenCalledWith({
        header_link_name: headerLink.headerLinkName,
      })
    }
  )
  it('should not display budget when user is readonly ', async () => {
    jest.spyOn(apiAdage, 'getEducationalInstitutionWithBudget')

    renderAdageHeader([], { ...user, role: AdageFrontRoles.READONLY })

    expect(apiAdage.getEducationalInstitutionWithBudget).not.toHaveBeenCalled()
  })
})
