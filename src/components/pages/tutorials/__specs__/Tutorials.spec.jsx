import React from 'react'
import FirstTutorial from '../FirstTutorial/FirstTutorial'
import { shallow } from 'enzyme'
import Tutorials from '../Tutorials'
import SecondTutorial from '../SecondTutorial/SecondTutorial'
import ThirdTutorial from '../ThirdTutorial/ThirdTutorial'

describe('components | Tutorials', () => {
  const history = { push: jest.fn() }
  const props = { history }

  describe('navigation', () => {
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
        const previousArrow = wrapper.find('.previous-arrow')
        expect(previousArrow).toHaveLength(0)
      })

      it('should display next arrow', () => {
        // when
        const wrapper = shallow(<Tutorials {...props} />)

        // Then
        const nextArrow = wrapper.find('.next-arrow')
        expect(nextArrow).toHaveLength(1)
      })
    })

    describe('when click on next arrow', () => {
      it('should display second tutorial', () => {
        // when
        const wrapper = shallow(<Tutorials {...props} />)
        wrapper.find('.next-arrow').simulate('click')

        // Then
        const secondTutorial = wrapper.find(SecondTutorial)
        expect(secondTutorial).toHaveLength(1)
      })

      it('should not display first tutorial', () => {
        // when
        const wrapper = shallow(<Tutorials {...props} />)
        wrapper.find('.next-arrow').simulate('click')

        // Then
        const firstTutorial = wrapper.find(FirstTutorial)
        expect(firstTutorial).toHaveLength(0)
      })

      it('should display previous and next arrow', () => {
        // when
        const wrapper = shallow(<Tutorials {...props} />)
        wrapper.find('.next-arrow').simulate('click')

        // Then
        const previousArrow = wrapper.find('.previous-arrow')
        const nextArrow = wrapper.find('.next-arrow')
        expect(previousArrow).toHaveLength(1)
        expect(nextArrow).toHaveLength(1)
      })

      describe('when click on previous arrow', () => {
        it('should display first tutorial', () => {
          // when
          const wrapper = shallow(<Tutorials {...props} />)
          wrapper.find('.next-arrow').simulate('click')
          wrapper.find('.previous-arrow').simulate('click')

          // Then
          const firstTutorial = wrapper.find(FirstTutorial)
          expect(firstTutorial).toHaveLength(1)
        })

        it('should not display second tutorial', () => {
          // when
          const wrapper = shallow(<Tutorials {...props} />)
          wrapper.find('.next-arrow').simulate('click')
          wrapper.find('.previous-arrow').simulate('click')

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
        wrapper.find('.next-arrow').simulate('click')
        wrapper.find('.next-arrow').simulate('click')

        // Then
        const thirdTutorial = wrapper.find(ThirdTutorial)
        expect(thirdTutorial).toHaveLength(1)
      })

      it('should not display second tutorial', () => {
        // when
        const wrapper = shallow(<Tutorials {...props} />)
        wrapper.find('.next-arrow').simulate('click')
        wrapper.find('.next-arrow').simulate('click')

        // Then
        const secondTutorial = wrapper.find(SecondTutorial)
        expect(secondTutorial).toHaveLength(0)
      })

      describe('when click on previous arrow', () => {
        it('should display second tutorial', () => {
          // when
          const wrapper = shallow(<Tutorials {...props} />)
          wrapper.find('.next-arrow').simulate('click')
          wrapper.find('.next-arrow').simulate('click')
          wrapper.find('.previous-arrow').simulate('click')

          // Then
          const secondTutorial = wrapper.find(SecondTutorial)
          expect(secondTutorial).toHaveLength(1)
        })

        it('should not display third tutorial', () => {
          // when
          const wrapper = shallow(<Tutorials {...props} />)
          wrapper.find('.next-arrow').simulate('click')
          wrapper.find('.next-arrow').simulate('click')
          wrapper.find('.previous-arrow').simulate('click')

          // Then
          const thirdTutorial = wrapper.find(ThirdTutorial)
          expect(thirdTutorial).toHaveLength(0)
        })
      })
    })

    describe('when click on next arrow three times', () => {
      it('should redirect to /decouverte', () => {
        // when
        const wrapper = shallow(<Tutorials {...props} />)

        wrapper.find('.next-arrow').simulate('click')
        wrapper.find('.next-arrow').simulate('click')
        wrapper.find('.next-arrow').simulate('click')

        // then
        expect(history.push).toHaveBeenCalledWith('/decouverte')
      })
    })
  })
})
