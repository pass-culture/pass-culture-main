import { mount } from 'enzyme'
import React from 'react'
import { act } from 'react-dom/test-utils'
import { MemoryRouter } from 'react-router'
import { campaignTracker } from '../../../../tracking/mediaCampaignsTracking'

import { checkIfAgeIsEligible } from '../domain/checkIfAgeIsEligible'
import { checkIfDepartmentIsEligible } from '../domain/checkIfDepartmentIsEligible'
import EligibilityCheck from '../EligibilityCheck'

jest.mock('../domain/checkIfAgeIsEligible', () => {
  const originalModule = jest.requireActual('../domain/checkIfAgeIsEligible')

  return {
    ...originalModule,
    checkIfAgeIsEligible: jest.fn(),
  }
})

jest.mock('../domain/checkIfDepartmentIsEligible', () => {
  const originalModule = jest.requireActual('../domain/checkIfDepartmentIsEligible')

  return {
    ...originalModule,
    checkIfDepartmentIsEligible: jest.fn(),
  }
})

describe('eligibility check page', () => {
  let props
  let trackEligibility
  const getFullYear = Date.prototype.getFullYear

  beforeEach(() => {
    Date.prototype.getFullYear = () => 2020
    trackEligibility = jest.fn()
    props = {
      history: {
        location: {
          hash: '',
        },
        replace: jest.fn(),
      },
      trackEligibility,
      isIdCheckAvailable: true,
      // FIXME (dbaty, 2020-01-18): once the feature flag is removed, delete or simplify
      // tests that have the "[legacy]" tag. (Other tests will have to be adapted, too.)
      wholeFranceOpening: false,
    }
  })

  afterEach(() => {
    Date.prototype.getFullYear = getFullYear
    jest.clearAllMocks()
  })

  describe('when rendering', () => {
    it('should display the title "Créer un compte"', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // then
      const eligibilityTitle = wrapper.find({ children: 'Créer un compte' })
      expect(eligibilityTitle).toHaveLength(1)
    })

    it('should display a back to beta page link', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // then
      const backLink = wrapper.find('a[href="/beta"]')
      expect(backLink).toHaveLength(1)
    })

    it('[legacy] should display a postal code input label', () => {
      // when
      props.wholeFranceOpening = false
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // then
      const eligibilityPostalCodeInputLabel = wrapper.find('label').at(0).text()
      expect(eligibilityPostalCodeInputLabel).toBe('Quel est ton code postal de résidence ?')
    })

    it('should only display a date of birth input label', () => {
      // when
      props.wholeFranceOpening = true
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // then
      const labels = wrapper.find('label')
      expect(labels).toHaveLength(1)
      const label = labels.at(0).text()
      expect(label).toBe('Quelle est ta date de naissance ?')
    })

    it('should display a date of birth input label', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // then
      const eligibilityDobInputLabel = wrapper.find('label').last().text()
      expect(eligibilityDobInputLabel).toBe('Quelle est ta date de naissance ?')
    })

    it('should display links to google recaptcha privacy and terms', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // then
      const googlePrivacyLink = wrapper.find('a[href="https://policies.google.com/privacy"]')
      const googleTermsLink = wrapper.find('a[href="https://policies.google.com/terms"]')
      expect(googlePrivacyLink).toHaveLength(1)
      expect(googleTermsLink).toHaveLength(1)
    })

    it('should display a submit button', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // then
      const eligibilitySubmitBtn = wrapper.find('input[value="Vérifier mon éligibilité"]')
      expect(eligibilitySubmitBtn).toHaveLength(1)
    })

    it('should not have a hash in url', () => {
      // given
      props.history.location.hash = '#fake-hash'

      // when
      mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // then
      expect(props.history.replace).toHaveBeenCalledWith({ hash: '' })
    })

    it('should append tag script', () => {
      // given
      jest.spyOn(document, 'querySelector').mockReturnValue({
        appendChild: jest.fn(),
      })
      const script = document.createElement('script')
      script.src = '/ebOneTag.js'

      // when
      mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // then
      expect(document.querySelector('body').appendChild).toHaveBeenCalledWith(script)
    })

    it('should call media campaign tracker on mount only', () => {
      // when mount
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // Then
      expect(campaignTracker.eligibilityCheck).toHaveBeenCalledTimes(1)

      // when rerender
      wrapper.setProps({})

      // Then
      expect(campaignTracker.eligibilityCheck).toHaveBeenCalledTimes(1)
    })
  })

  describe('[legacy] when user fills in his postal code and / or date of birth', () => {
    it('should add a space in input when user enters the first two numbers of his postal code', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )
      const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')

      // when
      act(() => {
        eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '76530' } })
      })
      wrapper.update()

      // then
      const eligibilityPostalCodeInputUpdated = wrapper.find('input[placeholder="Ex: 75017"]')
      expect(eligibilityPostalCodeInputUpdated.prop('value')).toBe('76530')
    })

    it('should add slashes in date of birth input', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )
      const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

      // when
      act(() => {
        eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05031997' } })
      })
      wrapper.update()

      // then
      const eligibilityDateOfBirthInputUpdated = wrapper.find('input[placeholder="JJ/MM/AAAA"]')
      expect(eligibilityDateOfBirthInputUpdated.prop('value')).toBe('05/03/1997')
    })

    it('should not display mask if user hasnt fill dob input yet', () => {
      // when
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      // then
      const dateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')
      expect(dateOfBirthInput.prop('value')).toBe('')
    })

    it('should display mask once user starts entering their day of birth', () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )
      const dateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

      // when
      act(() => {
        dateOfBirthInput.invoke('onChange')({ target: { value: '1' } })
      })
      wrapper.update()

      // then
      const updatedDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')
      expect(updatedDateOfBirthInput.prop('value')).toBe('1_/__/____')
    })
  })

  describe('when user submits form', () => {
    it("should check if age is eligible based on user's date of birth", () => {
      // given
      const wrapper = mount(
        <MemoryRouter>
          <EligibilityCheck {...props} />
        </MemoryRouter>
      )

      const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
      const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')
      const dateOfBirth = '05/03/2002'

      act(() => {
        eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
        eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: dateOfBirth } })
      })
      wrapper.update()

      const eligibilityForm = wrapper.find('form')

      // when
      act(() => {
        eligibilityForm.invoke('onSubmit')({
          preventDefault: jest.fn(),
        })
      })
      wrapper.update()

      // then
      expect(checkIfAgeIsEligible).toHaveBeenCalledWith(dateOfBirth)
    })

    describe('when user age is eligible', () => {
      beforeEach(() => {
        checkIfAgeIsEligible.mockReturnValue('eligible')
      })

      it("[legacy] should check if department is eligible based on user's postal code", () => {
        // given
        checkIfAgeIsEligible.mockReturnValue('eligible')
        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')
        const postalCode = '93800'

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: postalCode } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/2002' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(checkIfDepartmentIsEligible).toHaveBeenCalledWith(postalCode)
      })

      describe('when ID check is activated', () => {
        it('should display eligible view', () => {
          // given
          props = { ...props }
          props.wholeFranceOpening = true

          const wrapper = mount(
            <MemoryRouter>
              <EligibilityCheck {...props} />
            </MemoryRouter>
          )

          const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

          act(() => {
            eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/2002' } })
          })
          wrapper.update()

          const eligibilityForm = wrapper.find('form')

          // when
          act(() => {
            eligibilityForm.invoke('onSubmit')({
              preventDefault: jest.fn(),
            })
          })
          wrapper.update()

          // then
          expect(wrapper.find({ children: 'Tu es éligible !' })).toHaveLength(1)
        })

        it('[legacy] should display eligible view when department is eligible', () => {
          // given
          checkIfDepartmentIsEligible.mockReturnValue(true)

          const wrapper = mount(
            <MemoryRouter>
              <EligibilityCheck {...props} />
            </MemoryRouter>
          )

          const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
          const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

          act(() => {
            eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
            eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/2002' } })
          })
          wrapper.update()

          const eligibilityForm = wrapper.find('form')

          // when
          act(() => {
            eligibilityForm.invoke('onSubmit')({
              preventDefault: jest.fn(),
            })
          })
          wrapper.update()

          // then
          expect(wrapper.find({ children: 'Tu es éligible !' })).toHaveLength(1)
        })
      })

      describe('when ID check is disabled', () => {
        it('should display the specific screen when department is eligible', () => {
          // given
          props.isIdCheckAvailable = false
          props.wholeFranceOpening = false
          checkIfDepartmentIsEligible.mockReturnValue(true)

          const wrapper = mount(
            <MemoryRouter>
              <EligibilityCheck {...props} />
            </MemoryRouter>
          )

          const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
          const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

          act(() => {
            eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
            eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/2002' } })
          })
          wrapper.update()

          const eligibilityForm = wrapper.find('form')

          // when
          act(() => {
            eligibilityForm.invoke('onSubmit')({
              preventDefault: jest.fn(),
            })
          })
          wrapper.update()

          // then
          expect(wrapper.find({ children: 'Oups !' })).toHaveLength(1)
          expect(
            wrapper.find({ children: 'Cette page est indisponible pour le moment.' })
          ).toHaveLength(1)
        })

        it('[legacy] should display the specific screen when department is eligible', () => {
          // given
          props.isIdCheckAvailable = false
          checkIfDepartmentIsEligible.mockReturnValue(true)

          const wrapper = mount(
            <MemoryRouter>
              <EligibilityCheck {...props} />
            </MemoryRouter>
          )

          const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
          const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

          act(() => {
            eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
            eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/2002' } })
          })
          wrapper.update()

          const eligibilityForm = wrapper.find('form')

          // when
          act(() => {
            eligibilityForm.invoke('onSubmit')({
              preventDefault: jest.fn(),
            })
          })
          wrapper.update()

          // then
          expect(wrapper.find({ children: 'Oups !' })).toHaveLength(1)
          expect(
            wrapper.find({ children: 'Cette page est indisponible pour le moment.' })
          ).toHaveLength(1)
        })
      })

      it('[legacy] should display ineligible department view when department is not eligible', () => {
        // given
        checkIfDepartmentIsEligible.mockReturnValue(false)

        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '27200' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/2002' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(
          wrapper.find({ children: 'Bientôt disponible dans ton département !' })
        ).toHaveLength(1)
        expect(props.history.replace).toHaveBeenCalledWith({ hash: '#departement-ineligible' })
      })
    })

    describe('when user age is not eligible', () => {
      beforeEach(() => {
        checkIfDepartmentIsEligible.mockReturnValue(true)
      })

      it('should display eligible soon view when user is soon to be eligible', () => {
        // given
        checkIfAgeIsEligible.mockReturnValue('soon')

        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/2003' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(wrapper.find({ children: 'C’est pour bientôt !' })).toHaveLength(1)
      })

      it('should display ineligible over eighteen view when user is not eligible anymore', () => {
        // given
        checkIfAgeIsEligible.mockReturnValue('tooOld')

        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/1997' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(wrapper.find({ children: 'Tu as plus de 18 ans' })).toHaveLength(1)
        expect(props.history.replace).toHaveBeenCalledWith({ hash: '#trop-age' })
      })

      it('should display ineligible under eighteen view when user is not eligible yet', () => {
        // given
        checkIfAgeIsEligible.mockReturnValue('tooYoung')

        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/2005' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(
          wrapper.find({
            children:
              'Il est encore un peu tôt pour toi. Pour profiter du pass Culture, tu dois avoir 18 ans.',
          })
        ).toHaveLength(1)
        expect(props.history.replace).toHaveBeenCalledWith({ hash: '#trop-jeune' })
      })
    })

    describe('when checking date', () => {
      beforeEach(() => {
        checkIfDepartmentIsEligible.mockReturnValue(true)
      })

      it('should display an error message when day is not between 01 and 31', () => {
        // given
        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '99/02/2002' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(wrapper.find({ children: 'Le format de la date est incorrect.' })).toHaveLength(1)
      })

      it('should display an error message when month is not between 01 and 12', () => {
        // given
        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '03/99/2002' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(wrapper.find({ children: 'Le format de la date est incorrect.' })).toHaveLength(1)
      })

      it('should display an error message when birth year is over current year', () => {
        // given
        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/02/2021' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(wrapper.find({ children: 'Le format de la date est incorrect.' })).toHaveLength(1)
      })

      it('should display an error message when birth year is 0000', () => {
        // given
        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/02/0000' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(wrapper.find({ children: 'Le format de la date est incorrect.' })).toHaveLength(1)
      })
    })

    describe('should track the eligibility result', () => {
      beforeEach(() => {
        checkIfDepartmentIsEligible.mockReturnValue(true)
      })

      it('with specific message when user is too old', () => {
        // given
        checkIfAgeIsEligible.mockReturnValue('tooOld')
        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93170' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/1997' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(props.trackEligibility).toHaveBeenCalledWith('Eligibilite - TooOld')
      })

      it('with specific message when user is too young', () => {
        // given
        checkIfAgeIsEligible.mockReturnValue('tooYoung')
        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/2005' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(props.trackEligibility).toHaveBeenCalledWith('Eligibilite - TooYoung')
      })

      it('with specific message when user is almost of age', () => {
        // given
        checkIfAgeIsEligible.mockReturnValue('soon')
        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '93800' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/03/2003' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(props.trackEligibility).toHaveBeenCalledWith('Eligibilite - Soon')
      })

      it('[legacy] with specific message when department is not eligible yet', () => {
        // given
        checkIfDepartmentIsEligible.mockReturnValue(false)
        checkIfAgeIsEligible.mockReturnValue('eligible')
        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '11111' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/02/2002' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(props.trackEligibility).toHaveBeenCalledWith('Eligibilite - WrongDepartment')
      })

      it('with specific message user is eligible', () => {
        // given
        checkIfDepartmentIsEligible.mockReturnValue(true)
        checkIfAgeIsEligible.mockReturnValue('eligible')
        const wrapper = mount(
          <MemoryRouter>
            <EligibilityCheck {...props} />
          </MemoryRouter>
        )

        const eligibilityPostalCodeInput = wrapper.find('input[placeholder="Ex: 75017"]')
        const eligibilityDateOfBirthInput = wrapper.find('input[placeholder="JJ/MM/AAAA"]')

        act(() => {
          eligibilityPostalCodeInput.invoke('onChange')({ target: { value: '11111' } })
          eligibilityDateOfBirthInput.invoke('onChange')({ target: { value: '05/02/2002' } })
        })
        wrapper.update()

        const eligibilityForm = wrapper.find('form')

        // when
        act(() => {
          eligibilityForm.invoke('onSubmit')({
            preventDefault: jest.fn(),
          })
        })
        wrapper.update()

        // then
        expect(props.trackEligibility).toHaveBeenCalledWith('Eligibilite - OK')
      })
    })
  })
})
