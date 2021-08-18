import { dehumanizeId, humanizeId } from '../dehumanizeId'

describe('dehumanizeId', () => {
  it.each`
    humanizedId  | dehumanizedId
    ${'8Q'}      | ${116}
    ${'AHEHK'}   | ${116853}
    ${'AHD3Q'}   | ${116664}
    ${'AHD3G'}   | ${116659}
    ${'AHD3C'}   | ${116657}
    ${'AGHYA'}   | ${102272}
    ${'A98K8'}   | ${138407}
    ${'MAYGK'}   | ${6303845}
    ${'AG8YRWQ'} | ${27101402}
    ${'B4GQA'}   | ${986368}
  `(
    'a given humanizedId: $humanizedId becomes a dehumanizedId: $dehumanizedId',
    ({ dehumanizedId, humanizedId }) => {
      expect(dehumanizeId(humanizedId)).toBe(dehumanizedId)
      expect(humanizeId(dehumanizedId)).toBe(humanizedId)
    }
  )
})
