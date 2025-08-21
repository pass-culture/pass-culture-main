import { getYupValidationSchemaErrors } from '@/commons/utils/yupValidationTestHelpers'

import type { IndividualOfferTimetableFormValues } from '../types'
import { validationSchema } from '../validationSchema'

const baseValidForm: IndividualOfferTimetableFormValues = {
    noEndDate: true,
    timetableType: 'calendar',
    openingHours: { MONDAY: [['12:12', '13:13']] },
    quantityPerPriceCategories: []
}

describe('validationSchema', () => {
    const cases: {
        description: string
        formValues: IndividualOfferTimetableFormValues
        expectedErrors: string[]
    }[] = [
            {
                description: 'valid form for the calendar type',
                formValues: baseValidForm,
                expectedErrors: [],
            },
            {
                description: 'invalid form for an openingHours type with no start date',
                formValues: { ...baseValidForm, timetableType: 'openingHours' },
                expectedErrors: ['La date de début est obligatoire'],
            },
            {
                description: 'invalid form for an openingHours type with no end date',
                formValues: { ...baseValidForm, timetableType: 'openingHours', noEndDate: false, startDate: '2050-01-01' },
                expectedErrors: ['La date de fin est obligatoire'],
            },
            {
                description: 'invalid form for an openingHours type with an end date before the start date',
                formValues: { ...baseValidForm, timetableType: 'openingHours', noEndDate: false, startDate: '2050-01-01', endDate: '2049-01-01' },
                expectedErrors: ['La date de fin ne peut pas être antérieure à la date de début'],
            },
            {
                description: 'invalid form for an openingHours type without opening hours',
                formValues: { ...baseValidForm, timetableType: 'openingHours', startDate: '2050-01-01', openingHours: null },
                expectedErrors: ['Les horaires d’ouverture sont obligatoires'],
            },
        ]

    cases.forEach(({ description, formValues, expectedErrors }) => {
        it(`should validate the form for case: ${description}`, async () => {
            const errors = await getYupValidationSchemaErrors(
                validationSchema,
                formValues
            )
            expect(errors).toEqual(expectedErrors)
        })
    })
})
