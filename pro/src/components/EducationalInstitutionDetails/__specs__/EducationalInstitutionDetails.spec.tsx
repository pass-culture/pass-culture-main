import { screen } from '@testing-library/react'

import { renderWithProviders } from 'commons/utils/renderWithProviders'

import { EducationalInstitutionDetails, EducationalInstitutionDetailsProps } from '../EducationalInstititutionDetails'

describe('EducationalInstitutionDetails', () => {
    const educationalInstitution = {
        id: 1,
        phoneNumber: '0600000000',
        institutionId: '0290063L',
        name: 'Mon Établissement scolaire',
        postalCode: '75000',
        city: 'Paris',
        institutionType: 'Établissement scolaire',
    }
    const teacher = {
        firstName: 'Alice',
        lastName: 'Teacher',
        email: 'alice.teacher@example.com',
    }
    const educationalRedactor = {
        firstName: 'John',
        lastName: 'Doe',
        email: 'john.doe@example.com',
    }

    const render = (props: Partial<EducationalInstitutionDetailsProps> = {}, newLayout = true) => {
        return renderWithProviders(
            <EducationalInstitutionDetails
                educationalInstitution={educationalInstitution}
                newLayout={newLayout}
                {...props}
            />
        )
    }

    describe('newLayout = true', () => {
        it('renders with no teacher and no educationalRedactor', () => {
            render({}, true)
            expect(screen.getByText('Contact de l’établissement')).toBeInTheDocument()
            expect(screen.getByRole('img', { name: 'Adresse de l’établissement' })).toBeInTheDocument()
            expect(screen.getByText('Mon Établissement scolaire', { exact: false })).toBeInTheDocument()
            expect(screen.getByRole('img', { name: 'Téléphone' })).toBeInTheDocument()
            expect(screen.getByText('0600000000')).toBeInTheDocument()
            // Ne doit pas afficher les sections teacher ou redactor
            expect(screen.queryByText('Offre destinée à :')).not.toBeInTheDocument()
            expect(screen.queryByText('Offre préréservée par :')).not.toBeInTheDocument()
        })

        it('renders with only teacher', () => {
            render({ teacher }, true)
            expect(screen.getByText('Offre destinée à :')).toBeInTheDocument()
            expect(screen.getByText('Alice Teacher')).toBeInTheDocument()
            expect(screen.getByText('alice.teacher@example.com')).toBeInTheDocument()
            // Ne doit pas afficher la section redactor
            expect(screen.queryByText('Offre préréservée par :')).not.toBeInTheDocument()
        })

        it('renders with only educationalRedactor', () => {
            render({ educationalRedactor }, true)
            expect(screen.getByText('Offre préréservée par :')).toBeInTheDocument()
            expect(screen.getByText('John Doe')).toBeInTheDocument()
            expect(screen.getByText('john.doe@example.com')).toBeInTheDocument()
            // Ne doit pas afficher la section teacher
            expect(screen.queryByText('Offre destinée à :')).not.toBeInTheDocument()
        })

        it('renders with both teacher and educationalRedactor', () => {
            render({ teacher, educationalRedactor }, true)
            expect(screen.getByText('Offre destinée à :')).toBeInTheDocument()
            expect(screen.getByText('Alice Teacher')).toBeInTheDocument()
            expect(screen.getByText('alice.teacher@example.com')).toBeInTheDocument()
            expect(screen.getByText('Offre préréservée par :')).toBeInTheDocument()
            expect(screen.getByText('John Doe')).toBeInTheDocument()
            expect(screen.getByText('john.doe@example.com')).toBeInTheDocument()
        })
    })

    describe('newLayout = false', () => {
        it('renders old layout with no educationalRedactor', () => {
            render({}, false)
            expect(screen.getByText('Contact de l’établissement scolaire')).toBeInTheDocument()
            // Ne doit pas afficher de nom ou email
            expect(screen.queryByText('John Doe')).not.toBeInTheDocument()
            expect(screen.queryByText('alice.teacher@example.com')).not.toBeInTheDocument()
        })

        it('renders old layout with educationalRedactor', () => {
            render({ educationalRedactor }, false)
            expect(screen.getByText('Contact de l’établissement scolaire')).toBeInTheDocument()
            expect(screen.getByText('John Doe')).toBeInTheDocument()
            expect(screen.getByText('john.doe@example.com')).toBeInTheDocument()
            // Ne doit pas afficher la section teacher
            expect(screen.queryByText('Alice Teacher')).not.toBeInTheDocument()
        })

        it('renders old layout with both teacher and educationalRedactor (should only show redactor)', () => {
            render({ teacher, educationalRedactor }, false)
            expect(screen.getByText('Contact de l’établissement scolaire')).toBeInTheDocument()
            expect(screen.getByText('John Doe')).toBeInTheDocument()
            expect(screen.getByText('john.doe@example.com')).toBeInTheDocument()
            // Ne doit pas afficher la section teacher
            expect(screen.queryByText('Alice Teacher')).not.toBeInTheDocument()
        })
    })
})