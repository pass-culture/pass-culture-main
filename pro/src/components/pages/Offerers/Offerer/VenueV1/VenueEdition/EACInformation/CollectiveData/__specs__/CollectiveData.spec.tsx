import '@testing-library/jest-dom'

import { render, screen } from '@testing-library/react'
import React from 'react'

import { api } from 'apiClient/api'
import { GetVenueResponseModel } from 'apiClient/v1'

import CollectiveData from '../CollectiveData'

jest.mock('apiClient/api', () => ({
  api: { getEducationalPartners: jest.fn() },
}))

describe('CollectiveData', () => {
  const venue = {
    collectiveDescription: 'une description',
    collectiveDomains: [1, 2],
    collectiveEmail: 'mon@email.com',
    collectiveInterventionArea: null,
    collectiveLegalStatus: 2,
    collectiveNetwork: [],
    collectivePhone: '',
    collectiveStudents: ['Collège - 3e'],
    collectiveWebsite: undefined,
  } as unknown as GetVenueResponseModel // we only test for used fields

  beforeAll(() => {
    jest
      .spyOn(api, 'getEducationalPartners')
      .mockResolvedValue({ partners: [] })
  })

  it('should not display title field if value is empty', async () => {
    render(<CollectiveData venue={venue} />)

    expect(await screen.findAllByRole('heading', { level: 4 })).toHaveLength(5)
  })
})
