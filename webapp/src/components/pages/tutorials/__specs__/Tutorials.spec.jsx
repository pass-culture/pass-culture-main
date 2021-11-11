import React from 'react'
import FirstTutorial from '../FirstTutorial/FirstTutorial'
import { shallow } from 'enzyme'
import Tutorials from '../Tutorials'
import SecondTutorial from '../SecondTutorial/SecondTutorial'
import ThirdTutorial from '../ThirdTutorial/ThirdTutorial'

describe('components | Tutorials', () => {
  let props
  let isHomepageDisabled
  let saveUserHasSeenTutorials

  beforeEach(() => {
    isHomepageDisabled = true
    saveUserHasSeenTutorials = jest.fn()
    props = { isHomepageDisabled, saveUserHasSeenTutorials }
  })

  describe('when display for the first time', () => {
    it('should display first tutorial', () => {
      // when
      const wrapper = shallow(<Tutorials {...props} />)

      // Then
      const firstTutorial = wrapper.find(FirstTutorial)
      expect(firstTutorial).toHaveLength(1)
    })

    it('should not display previous arrow', () => {
      // when
      const wrapper = shallow(<Tutorials {...props} />)

      // Then
      const previousArrow = wrapper.find({ alt: 'Précédent' })
      expect(previousArrow).toHaveLength(0)
    })

    it('should display next arrow', () => {
      // when
      const wrapper = shallow(<Tutorials {...props} />)

      // Then
      const nextArrow = wrapper.find({ alt: 'Suivant' })
      expect(nextArrow).toHaveLength(1)
    })
  })

  describe('when click on next arrow', () => {
    it('should display second tutorial', () => {
      // when
      const wrapper = shallow(<Tutorials {...props} />)
      wrapper
        .find({ alt: 'Suivant' })
        .parent('button')
        .simulate('click')

      // Then
      const secondTutorial = wrapper.find(SecondTutorial)
      expect(secondTutorial).toHaveLength(1)
    })

    it('should not display first tutorial', () => {
      // when
      const wrapper = shallow(<Tutorials {...props} />)
      wrapper
        .find({ alt: 'Suivant' })
        .parent('button')
        .simulate('click')

      // Then
      const firstTutorial = wrapper.find(FirstTutorial)
      expect(firstTutorial).toHaveLength(0)
    })

    it('should display previous and next arrow', () => {
      // when
      const wrapper = shallow(<Tutorials {...props} />)
      wrapper
        .find({ alt: 'Suivant' })
        .parent('button')
        .simulate('click')

      // Then
      const previousArrow = wrapper.find({ alt: 'Précédent' })
      const nextArrow = wrapper.find({ alt: 'Suivant' })
      expect(previousArrow).toHaveLength(1)
      expect(nextArrow).toHaveLength(1)
    })

    describe('when click on previous arrow', () => {
      it('should display first tutorial', () => {
        // when
        const wrapper = shallow(<Tutorials {...props} />)
        wrapper
          .find({ alt: 'Suivant' })
          .parent('button')
          .simulate('click')
        wrapper
          .find({ alt: 'Précédent' })
          .parent('button')
          .simulate('click')

        // Then
        const firstTutorial = wrapper.find(FirstTutorial)
        expect(firstTutorial).toHaveLength(1)
      })

      it('should not display second tutorial', () => {
        // when
        const wrapper = shallow(<Tutorials {...props} />)
        wrapper
          .find({ alt: 'Suivant' })
          .parent('button')
          .simulate('click')
        wrapper
          .find({ alt: 'Précédent' })
          .parent('button')
          .simulate('click')

        // Then
        const secondTutorial = wrapper.find(SecondTutorial)
        expect(secondTutorial).toHaveLength(0)
      })
    })
  })

  describe('when click on next arrow twice', () => {
    it('should display third tutorial', () => {
      // when
      const wrapper = shallow(<Tutorials {...props} />)
      wrapper
        .find({ alt: 'Suivant' })
        .parent('button')
        .simulate('click')
      wrapper
        .find({ alt: 'Suivant' })
        .parent('button')
        .simulate('click')

      // Then
      const thirdTutorial = wrapper.find(ThirdTutorial)
      expect(thirdTutorial).toHaveLength(1)
    })

    it('should not display second tutorial', () => {
      // when
      const wrapper = shallow(<Tutorials {...props} />)
      wrapper
        .find({ alt: 'Suivant' })
        .parent('button')
        .simulate('click')
      wrapper
        .find({ alt: 'Suivant' })
        .parent('button')
        .simulate('click')

      // Then
      const secondTutorial = wrapper.find(SecondTutorial)
      expect(secondTutorial).toHaveLength(0)
    })

    describe('when click on previous arrow', () => {
      it('should display second tutorial', () => {
        // when
        const wrapper = shallow(<Tutorials {...props} />)
        wrapper
          .find({ alt: 'Suivant' })
          .parent('button')
          .simulate('click')
        wrapper
          .find({ alt: 'Suivant' })
          .parent('button')
          .simulate('click')
        wrapper
          .find({ alt: 'Précédent' })
          .parent('button')
          .simulate('click')

        // Then
        const secondTutorial = wrapper.find(SecondTutorial)
        expect(secondTutorial).toHaveLength(1)
      })

      it('should not display third tutorial', () => {
        // when
        const wrapper = shallow(<Tutorials {...props} />)
        wrapper
          .find({ alt: 'Suivant' })
          .parent('button')
          .simulate('click')
        wrapper
          .find({ alt: 'Suivant' })
          .parent('button')
          .simulate('click')
        wrapper
          .find({ alt: 'Précédent' })
          .parent('button')
          .simulate('click')

        // Then
        const thirdTutorial = wrapper.find(ThirdTutorial)
        expect(thirdTutorial).toHaveLength(0)
      })
    })
  })

  describe('when click on next arrow three times', () => {
    it('should save informations that user has finished to see the three tutorials and redirect to /decouverte', () => {
      // when
      const wrapper = shallow(<Tutorials {...props} />)

      for (let i = 1; i <= 3; i++) {
        wrapper
          .find({ alt: 'Suivant' })
          .parent('button')
          .simulate('click')
      }

      // then
      expect(saveUserHasSeenTutorials).toHaveBeenCalledWith(props.isHomepageDisabled)
    })
  })
})
