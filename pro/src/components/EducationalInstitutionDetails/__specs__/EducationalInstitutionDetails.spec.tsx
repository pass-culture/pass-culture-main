import { screen } from '@testing-library/react'

import { CollectiveBookingEducationalRedactorResponseModel, EducationalInstitutionResponseModel } from 'apiClient/v1'
import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { EducationalInstitutionDetails, EducationalInstitutionDetailsProps } from '../EducationalInstititutionDetails'

describe('CollectiveStatusLabel without educationalRedactor', () => {
    let props: EducationalInstitutionDetailsProps
    beforeEach(() => {
        const educationalInstitution: EducationalInstitutionResponseModel = {
            id: 1,
            phoneNumber: "0600000000",
            institutionId: "0290063L",
            name: 'Mon Établissement scolaire',
            postalCode: '75000',
            city: 'Paris',
            institutionType: 'Établissement scolaire',
        }

        props = {
            educationalInstitution,
        }
    })

    it(
        'should render without educationalRedactor',
        () => {

            renderWithProviders(
                <EducationalInstitutionDetails {...props} newLayout={true} />
            )
            expect(screen.getByText('Contact de l’établissement')).toBeInTheDocument()
            expect(screen.getByRole('img', { name: 'Adresse de l’établissement' })).toBeInTheDocument()
            expect(screen.getByText('Mon Établissement scolaire', { exact: false })).toBeInTheDocument()

            expect(screen.queryByRole('img', { name: 'Nom' })).not.toBeInTheDocument()
        }

    )

    it(
        'should render old layout',
        () => {

            renderWithProviders(
                <EducationalInstitutionDetails {...props} newLayout={false} />
            )
            expect(screen.getByText('Contact de l’établissement scolaire')).toBeInTheDocument()
        }
    )
})

describe('CollectiveStatusLabel with educationalRedactor', () => {
    let props: EducationalInstitutionDetailsProps
    beforeEach(() => {
        const educationalInstitution: EducationalInstitutionResponseModel = {
            id: 1,
            phoneNumber: "0600000000",
            institutionId: "0290063L",
            name: 'Mon Établissement scolaire',
            postalCode: '75000',
            city: 'Paris',
            institutionType: 'Établissement scolaire',
        }

        const educationalRedactor: CollectiveBookingEducationalRedactorResponseModel = {
            id: 1,
            firstName: 'John',
            lastName: 'Doe',
            email: 'john.doe@example.com',
        }

        props = {
            educationalInstitution,
            educationalRedactor,
        }
    })

    it(
        'should render with educationalRedactor',
        () => {

            renderWithProviders(
                <EducationalInstitutionDetails {...props} newLayout={true} />
            )
            expect(screen.getByText('Contact de l’établissement')).toBeInTheDocument()
            expect(screen.getByRole('img', { name: 'Adresse de l’établissement' })).toBeInTheDocument()
            expect(screen.getByText('Mon Établissement scolaire', { exact: false })).toBeInTheDocument()

            expect(screen.queryByRole('img', { name: 'Nom' })).toBeInTheDocument()
            expect(screen.getByText('John Doe')).toBeInTheDocument()
            expect(screen.getByText('john.doe@example.com')).toBeInTheDocument()
        }

    )

    it(
        'should render old layout',
        () => {

            renderWithProviders(
                <EducationalInstitutionDetails {...props} newLayout={false} />
            )
            expect(screen.getByText('Contact de l’établissement scolaire')).toBeInTheDocument()
        }
    )
})