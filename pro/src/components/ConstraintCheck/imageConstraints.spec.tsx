import { createImageFile } from 'commons/utils/testFileHelpers'

import { imageConstraints, getValidatorErrors } from './imageConstraints'

const mockCreateImageBitmap = vi.fn()

Object.defineProperty(global, 'createImageBitmap', {
  writable: true,
  value: mockCreateImageBitmap,
})

describe('image constraints', () => {
  describe('formats', () => {
    describe('checks file type', () => {
      it('accepts image with valid type', async () => {
        const file = createImageFile({ type: 'image/png' })
        const constraint = imageConstraints.formats(['image/png'])

        const isValid = await constraint.asyncValidator(file)

        expect(isValid).toBe(true)
      })

      it('refuses image with invalid type', async () => {
        const file = createImageFile({ type: 'image/jpeg' })
        const constraint = imageConstraints.formats(['image/png'])

        const isValid = await constraint.asyncValidator(file)

        expect(isValid).toBe(false)
      })
    })

    describe('checks file binary', () => {
      it('accepts bitmap image', async () => {
        const file = createImageFile()
        const constraint = imageConstraints.formats(['image/png'])

        const isValid = await constraint.asyncValidator(file)

        expect(isValid).toBe(true)
      })

      it('refuse non bitmap file', async () => {
        // TODO: replace Object.defineProperty with something that doesn't impact other tests/suites
        const file = createImageFile()
        const constraint = imageConstraints.formats(['image/png'])
        Object.defineProperty(global, 'createImageBitmap', {
          writable: true,
          value: vi.fn().mockRejectedValueOnce(null),
        })

        const isValid = await constraint.asyncValidator(file)

        expect(isValid).toBe(false)
      })
    })
  })

  describe('size', () => {
    it("accepts image when it's lighter that maximum", async () => {
      const file = createImageFile({ sizeInMB: 1 })
      const constraint = imageConstraints.size(1024 ** 2)

      const isValid = await constraint.asyncValidator(file)

      expect(isValid).toBe(true)
    })

    it("refuses image when it's heavier than maximum", async () => {
      const file = createImageFile({ sizeInMB: 1 })
      const constraint = imageConstraints.size(1024 ** 2 - 1)

      const isValid = await constraint.asyncValidator(file)

      expect(isValid).toBe(false)
    })
  })

  describe('height', () => {
    it("accepts image when it's higher than minimum", async () => {
      const file = createImageFile({ height: 400 })
      const constraint = imageConstraints.height(400)

      const isValid = await constraint.asyncValidator(file)

      expect(isValid).toBe(true)
    })

    it("refuses image when it's smaller than minimum", async () => {
      const file = createImageFile({ width: 400 })
      const constraint = imageConstraints.height(300)

      const isValid = await constraint.asyncValidator(file)

      expect(isValid).toBe(false)
    })

    it('refuses when no min height', async () => {
      const file = createImageFile({ width: 400 })
      const constraint = imageConstraints.height()

      const isValid = await constraint.asyncValidator(file)

      expect(isValid).toBe(false)
    })
  })
})

describe('width', () => {
  it("accepts image when it's larger that minimum", async () => {
    const file = createImageFile({ width: 300 })
    const constraint = imageConstraints.width(300)

    const isValid = await constraint.asyncValidator(file)

    expect(isValid).toBe(true)
  })

  it("refuses image when it's smaller than minimum", async () => {
    const file = createImageFile({ width: 200 })
    const constraint = imageConstraints.width(300)

    const isValid = await constraint.asyncValidator(file)

    expect(isValid).toBe(false)
  })
})

describe('getValidatorErrors', () => {
  it('reports name of the constraints that are not respected', async () => {
    const constraints = [
      imageConstraints.formats(['image/png']),
      imageConstraints.width(300),
    ]
    const file = createImageFile({
      type: 'image/png',
      width: 200,
      height: 200,
    })

    const failedConstraints = await getValidatorErrors(constraints, file)

    expect(failedConstraints).toStrictEqual(['width'])
  })
})
