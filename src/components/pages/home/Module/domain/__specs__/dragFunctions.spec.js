import { calculatePositionX, calculateStep } from '../dragFunctions'

describe('src | dragFunctions', () => {
  describe('calculatePositionX', () => {
    describe('when moving right', () => {
      it('should return new position translated to right when step inferior to max steps', () => {
        // given
        const parameters = {
          lastX: 1,
          maxSteps: 3,
          newX: 0.5,
          step: 1,
          width: 100
        }

        // when
        const positionX = calculatePositionX(parameters)

        // then
        expect(positionX).toBe(-102.49999999999999)
      })

      it('should return last x when step is equal to maxSteps', () => {
        // given
        const parameters = {
          lastX: 1,
          maxSteps: 3,
          newX: 0.5,
          step: 3,
          width: 100
        }

        // when
        const positionX = calculatePositionX(parameters)

        // then
        expect(positionX).toBe(1)
      })
    })

    describe('when moving left', () => {
      it('should return new position translated to left when step is superior to default step', () => {
        // given
        const parameters = {
          lastX: 1,
          maxSteps: 3,
          newX: 2,
          step: 2,
          width: 100
        }

        // when
        const positionX = calculatePositionX(parameters)

        // then
        expect(positionX).toBe(104.49999999999999)
      })

      it('should return default position when step is equal to default step', () => {
        // given
        const parameters = {
          lastX: 1,
          maxSteps: 3,
          newX: 2,
          step: 1,
          width: 100
        }

        // when
        const positionX = calculatePositionX(parameters)

        // then
        expect(positionX).toBe(0)
      })
    })
  })

  describe('calculateStep', () => {
    describe('when moving right', () => {
      it('should return step incremented by one when step is inferior to max steps', () => {
        // given
        const parameters = {
          lastX: 2,
          maxSteps: 5,
          newX: 1,
          step: 1
        }

        // when
        const step = calculateStep(parameters)

        // then
        expect(step).toBe(2)
      })

      it('should max steps when step is equal to max steps', () => {
        // given
        const parameters = {
          lastX: 2,
          maxSteps: 5,
          newX: 1,
          step: 5
        }

        // when
        const step = calculateStep(parameters)

        // then
        expect(step).toBe(5)
      })
    })

    describe('when moving left', () => {
      it('should return step decremented by one when step is superior to default step', () => {
        // given
        const parameters = {
          lastX: 1,
          maxSteps: 5,
          newX: 2,
          step: 5
        }

        // when
        const step = calculateStep(parameters)

        // then
        expect(step).toBe(4)
      })

      it('should return default step when step is equal to default step', () => {
        // given
        const parameters = {
          lastX: 1,
          maxSteps: 5,
          newX: 2,
          step: 1
        }

        // when
        const step = calculateStep(parameters)

        // then
        expect(step).toBe(1)
      })
    })
  })
})
