import { getYupValidationSchemaErrors } from 'utils/yupValidationTestHelpers'

import { generateValidationSchema } from '../validationSchema'

describe('validationSchema', () => {
  const values = {
    startDatetime: '2024-09-01',
    endDatetime: '2024-09-01',
    bookingLimitDatetime: '2024-09-01',
    eventTime: '05:05',
    numberOfPlaces: '56',
    priceDetail: 'Détails sur le prix',
    totalPrice: '1500',
  }

  it('should generate an error when start date and end date are not in the same school year', async () => {
    const formValues = {
      ...values,
      startDatetime: '2024-09-01',
      endDatetime: '2025-09-01',
    }

    const errors = await getYupValidationSchemaErrors(
      generateValidationSchema(false, 0),
      formValues
    )
    expect(errors).toEqual([
      'Les dates doivent être sur la même année scolaire',
    ])
  })

  it('should allow a start datetime set on 01/09/N and an end datetime set on 31/08/N+1', async () => {
    const formValues = {
      ...values,
      startDatetime: '2024-09-01',
      endDatetime: '2025-08-31',
    }

    const errors = await getYupValidationSchemaErrors(
      generateValidationSchema(false, 0),
      formValues
    )
    expect(errors).toEqual([])
  })
})
