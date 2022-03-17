import '@testing-library/jest-dom'
import { shallow } from 'enzyme'
import React from 'react'
import { Field } from 'react-final-form'

import { validateSiret } from 'core/Venue/validate'
import TextareaField from 'components/layout/form/fields/TextareaField'
import TextField from 'components/layout/form/fields/TextField'

import VenueLabel from '../../../ValueObjects/VenueLabel'
import VenueType from '../../../ValueObjects/VenueType'
import IdentifierFields from '../IdentifierFields'

describe('src | components | pages | Venue | fields | IdentifierFields', () => {
  let props

  beforeEach(() => {
    props = {
      fieldReadOnlyBecauseFrozenFormSiret: true,
      formSiret: 'form siret',
      initialSiret: 'form siret',
      isCreatedEntity: true,
      isModifiedEntity: true,
      readOnly: true,
      venueTypes: [],
      venueTypeCode: null,
      venueLabels: [],
      venueLabelId: null,
    }
  })

  describe('render', () => {
    it('should display four TextField and one TextAreaField components with the right props', () => {
      // given
      const props = {
        fieldReadOnlyBecauseFrozenFormSiret: false,
        initialSiret: null,
        isCreatedEntity: true,
        isModifiedEntity: true,
        readOnly: true,
        venueTypes: [],
        venueLabels: [],
      }

      // when
      const wrapper = shallow(<IdentifierFields {...props} />)

      // then
      const mainListTitle = wrapper.find('.main-list-title')
      expect(mainListTitle).toHaveLength(1)
      expect(mainListTitle.text()).toBe('Informations lieu')

      const textFields = wrapper.find(TextField)
      expect(textFields).toHaveLength(4)

      const textareaField = wrapper.find(TextareaField)
      expect(textareaField).toHaveLength(2)

      expect(textFields.at(0).prop('name')).toBe('siret')
      expect(textFields.at(0).prop('required')).toBe(false)

      expect(textFields.at(1).prop('label')).toBe('Nom du lieu : ')
      expect(textFields.at(1).prop('name')).toBe('name')
      expect(textFields.at(1).prop('required')).toBe(true)

      expect(textFields.at(2).prop('label')).toBe('Nom d’usage du lieu : ')
      expect(textFields.at(2).prop('name')).toBe('publicName')
      expect(textFields.at(2).prop('required')).toBe(false)

      expect(textFields.at(3).prop('label')).toBe('Mail : ')
      expect(textFields.at(3).prop('name')).toBe('bookingEmail')
      expect(textFields.at(3).prop('required')).toBe(true)

      expect(textareaField.at(0).prop('label')).toBe(
        'Commentaire (si pas de SIRET) : '
      )
      expect(textareaField.at(0).prop('name')).toBe('comment')

      expect(textareaField.at(1).prop('label')).toBe('Description : ')
      expect(textareaField.at(1).prop('name')).toBe('description')
    })

    describe('siret text field', () => {
      it('siret TextField can be edited when mode is not readOnly and there is no initial siret', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isModifiedEntity: true,
          initialSiret: null,
          readOnly: false,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textFields = wrapper.find(TextField)
        expect(textFields.at(0).prop('name')).toBe('siret')
        expect(textFields.at(0).prop('readOnly')).toBe(false)
      })

      it('siret TextField cannot be edited when mode is read only', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isEntrepriseApiDisabled: false,
          isModifiedEntity: true,
          readOnly: true,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textFields = wrapper.find(TextField)
        expect(textFields.at(0).prop('name')).toBe('siret')
        expect(textFields.at(0).prop('readOnly')).toBe(true)
      })

      it('proper siret label is returned when isCreatedEntity is true', () => {
        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const siretField = wrapper.find(TextField).at(0)
        expect(siretField.prop('label')).toBe(
          'SIRET du lieu qui accueille vos offres (si applicable) : '
        )
      })

      it('proper siret validate is returned when initialSiret is null and Entreprise Api not disabled', () => {
        props.isEntrepriseApiDisabled = false
        props.initialSiret = null
        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const siretField = wrapper.find(TextField).at(0)
        expect(siretField.prop('validate')).toBe(validateSiret)
      })

      it('proper siret validate is null when Entreprise Api is disabled', () => {
        props.isEntrepriseApiDisabled = true
        props.initialSiret = null
        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const siretField = wrapper.find(TextField).at(0)
        expect(siretField.prop('validate')).toBeNull()
      })

      it('proper siret label is returned when isCreatedEntity is false', () => {
        // given
        const props = {
          isCreatedEntity: false,
          isModifiedEntity: true,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const siretField = wrapper.find(TextField).at(0)
        expect(siretField.prop('label')).toBe('SIRET : ')
      })
    })

    describe('name text field', () => {
      it('name TextField can be edited when mode is not readOnly and fieldReadOnlyBecauseFrozenFormSiretdisplay is false', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isModifiedEntity: true,
          fieldReadOnlyBecauseFrozenFormSiret: false,
          readOnly: false,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textFields = wrapper.find(TextField)
        expect(textFields.at(1).prop('name')).toBe('name')
        expect(textFields.at(1).prop('readOnly')).toBe(false)
      })

      it('name TextField cannot be edited when mode is read only', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isModifiedEntity: true,
          readOnly: true,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textFields = wrapper.find(TextField)
        expect(textFields.at(1).prop('name')).toBe('name')
        expect(textFields.at(1).prop('readOnly')).toBe(true)
      })

      it('name TextField cannot be edited when fieldReadOnlyBecauseFrozenFormSiretdisplay is tue', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isModifiedEntity: true,
          fieldReadOnlyBecauseFrozenFormSiretdisplay: true,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textFields = wrapper.find(TextField)
        expect(textFields.at(1).prop('name')).toBe('name')
        expect(textFields.at(1).prop('readOnly')).toBe(true)
      })
    })

    describe('publicName text field', () => {
      it('publicName TextField can be edited when mode is not readOnly', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isModifiedEntity: true,
          fieldReadOnlyBecauseFrozenFormSiret: false,
          readOnly: false,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textFields = wrapper.find(TextField)
        expect(textFields.at(2).prop('name')).toBe('publicName')
        expect(textFields.at(2).prop('readOnly')).toBe(false)
      })

      it('publicName TextField cannot be edited when mode is read only', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isModifiedEntity: true,
          readOnly: true,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textFields = wrapper.find(TextField)
        expect(textFields.at(2).prop('name')).toBe('publicName')
        expect(textFields.at(2).prop('readOnly')).toBe(true)
      })
    })

    describe('email text field', () => {
      it('email TextField can be edited when mode is not readOnly', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isModifiedEntity: true,
          fieldReadOnlyBecauseFrozenFormSiret: false,
          readOnly: false,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textFields = wrapper.find(TextField)
        expect(textFields.at(3).prop('name')).toBe('bookingEmail')
        expect(textFields.at(3).prop('readOnly')).toBe(false)
      })

      it('email TextField cannot be edited when mode is read only', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isModifiedEntity: true,
          readOnly: true,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textFields = wrapper.find(TextField)
        expect(textFields.at(3).prop('name')).toBe('bookingEmail')
        expect(textFields.at(3).prop('readOnly')).toBe(true)
      })
    })

    describe('comment text area field', () => {
      it('comment text area field can be edited when mode is not readOnly', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isModifiedEntity: true,
          readOnly: false,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textareaField = wrapper.find(TextareaField)
        expect(textareaField.at(0).prop('name')).toBe('comment')
        expect(textareaField.at(0).prop('readOnly')).toBe(false)
      })

      it('comment text area field cannot be edited when mode is read only', () => {
        // given
        const props = {
          isCreatedEntity: true,
          isModifiedEntity: true,
          readOnly: true,
          venueTypes: [],
          venueLabels: [],
        }

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const textareaField = wrapper.find(TextareaField)
        expect(textareaField.at(0).prop('name')).toBe('comment')
        expect(textareaField.at(0).prop('readOnly')).toBe(true)
      })

      it('should not validate comment field when no siret have been provided', () => {
        // given
        props.formSiret = null

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const commentField = wrapper.find(TextareaField).at(0)
        expect(commentField.prop('validate')()).toBe('Ce champ est obligatoire')
      })

      it('should not validate empty comment field when siret length does not match 14 characters', () => {
        // given
        props.formSiret = 'AAA'

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const commentField = wrapper.find(TextareaField).at(0)
        expect(commentField.prop('validate')()).toBe('Ce champ est obligatoire')
      })

      it('should validate empty comment field when siret is provided and valid', () => {
        // given
        props.formSiret = '41816609600068'

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const commentField = wrapper.find(TextareaField).at(0)
        expect(commentField.prop('validate')()).toBe('')
      })
    })

    describe('type of venue field', () => {
      describe('when the form is in edition mode', () => {
        it('should be editable', () => {
          // Given
          props.readOnly = false
          props.venueTypes = [
            new VenueType({ id: 'A1', label: "Centre d'art et d'essais" }),
          ]

          // When
          const wrapper = shallow(<IdentifierFields {...props} />)

          // Then
          const selectField = wrapper
            .find(Field)
            .findWhere(node => node.prop('id') === 'venue-type')
          expect(selectField.prop('disabled')).toBeUndefined()
        })

        it('should have a list of options with venue types', () => {
          // Given
          props.readOnly = false
          props.venueTypes = [
            new VenueType({ id: 'A1', label: "Centre d'art et d'essais" }),
          ]

          // When
          const wrapper = shallow(<IdentifierFields {...props} />)

          // Then
          const selectField = wrapper
            .find(Field)
            .findWhere(node => node.prop('id') === 'venue-type')
          expect(selectField.prop('component')).toBe('select')

          const venueTypeOptions = wrapper.find('option')
          expect(venueTypeOptions.at(0).text()).toBe(
            'Choisissez un type de lieu dans la liste'
          )
          expect(venueTypeOptions.at(1).text()).toBe("Centre d'art et d'essais")
        })
      })

      describe('when the form is in display mode', () => {
        describe('when no venue type has been chosen', () => {
          it('should not exist', () => {
            // Given
            props.readOnly = true
            props.venueTypeCode = null
            props.venueTypes = [
              new VenueType({ id: 'A1', label: "Centre d'art et d'essais" }),
            ]

            // When
            const wrapper = shallow(<IdentifierFields {...props} />)

            // Then
            const selectField = wrapper
              .find(Field)
              .findWhere(node => node.prop('id') === 'venue-type')
            expect(selectField).toHaveLength(0)
          })
        })

        describe('when venue type is defined', () => {
          it('should display the label', () => {
            // Given
            props.readOnly = true
            props.venueTypeCode = 'A1'
            props.venueTypes = [
              new VenueType({ id: 'A1', label: "Centre d'art et d'essais" }),
            ]

            // When
            const wrapper = shallow(<IdentifierFields {...props} />)

            // Then
            const venueTypeLabel = wrapper
              .findWhere(node => node.prop('id') === 'venue-type')
              .find('span')
            expect(venueTypeLabel.text()).toBe("Centre d'art et d'essais")
          })
        })
      })

      it('should not validate select field when no venue type have been selected', () => {
        // given
        props.readOnly = false

        // when
        const wrapper = shallow(<IdentifierFields {...props} />)

        // then
        const selectField = wrapper
          .find(Field)
          .findWhere(node => node.prop('id') === 'venue-type')
        expect(selectField.prop('validate')()).toBe('Ce champ est obligatoire')
        const venueTypeOptions = wrapper.find('option')
        expect(venueTypeOptions.at(0).text()).toBe(
          'Choisissez un type de lieu dans la liste'
        )
      })
    })

    describe('label of venue field', () => {
      describe('when the form is in edition mode', () => {
        it('should be editable', () => {
          // Given
          props.readOnly = false
          props.venueLabels = [
            new VenueLabel({
              id: 'A1',
              label: "CAC - Centre d'art contemporain d'intérêt national",
            }),
          ]

          // When
          const wrapper = shallow(<IdentifierFields {...props} />)

          // Then
          const selectField = wrapper
            .find(Field)
            .findWhere(node => node.prop('id') === 'venue-label')
          expect(selectField.prop('disabled')).toBeUndefined()
        })

        it('should have a list of options with venue labels', () => {
          // Given
          props.readOnly = false
          props.venueLabels = [
            new VenueLabel({
              id: 'A1',
              label: "CAC - Centre d'art contemporain d'intérêt national",
            }),
          ]

          // When
          const wrapper = shallow(<IdentifierFields {...props} />)

          // Then
          const selectField = wrapper
            .find(Field)
            .findWhere(node => node.prop('id') === 'venue-label')
          expect(selectField.prop('component')).toBe('select')

          const venueLabelOptions = selectField.find('option')
          expect(venueLabelOptions.at(0).text()).toBe(
            'Si votre lieu est labellisé précisez-le en le sélectionnant dans la liste'
          )
          expect(venueLabelOptions.at(1).text()).toBe(
            "CAC - Centre d'art contemporain d'intérêt national"
          )
        })
      })

      describe('when the form is in display mode', () => {
        describe('when no venue label has been chosen', () => {
          it('should not exist', () => {
            // Given
            props.readOnly = true
            props.venueLabelId = null
            props.venueLabels = [
              new VenueLabel({
                id: 'A1',
                label: "CAC - Centre d'art contemporain d'intérêt national",
              }),
            ]

            // When
            const wrapper = shallow(<IdentifierFields {...props} />)

            // Then
            const selectField = wrapper
              .find(Field)
              .findWhere(node => node.prop('id') === 'venue-label')
            expect(selectField).toHaveLength(0)
          })
        })

        describe('when venue label is defined', () => {
          it('should be disabled', () => {
            // Given
            props.readOnly = true
            props.venueLabelId = 'A1'
            props.venueLabels = [
              new VenueLabel({
                id: 'A1',
                label: "CAC - Centre d'art contemporain d'intérêt national",
              }),
            ]

            // When
            const wrapper = shallow(<IdentifierFields {...props} />)

            // Then
            const venueLabelText = wrapper
              .findWhere(node => node.prop('id') === 'venue-label')
              .find('span')
            expect(venueLabelText.text()).toBe(
              "CAC - Centre d'art contemporain d'intérêt national"
            )
          })
        })
      })
    })
  })
})
