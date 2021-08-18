import { decode, encode } from 'hi-base32'

export const dehumanizeId = humanId => {
  try {
    return byteArrayToInt(decode.asBytes(humanId.replace(/8/g, 'O').replace(/9/g, 'I')))
  } catch (e) {
    return null
  }
}

const byteArrayToInt = bytes =>
  bytes.reduce((result, byte, index) => result + byte * Math.pow(256, bytes.length - 1 - index), 0)

const intToByteArray = x => {
  const byteArray = [x, x << 8, x << 16, x << 24].map(z => z >>> 24)
  //we want to remove all bytes equal to 0 if they are at the beginning of the array
  while (byteArray[0] === 0) {
    byteArray.shift()
  }
  return byteArray
}

export const humanizeId = dehumanizedId => {
  try {
    return encode(intToByteArray(dehumanizedId))
      .replace(/O/g, '8')
      .replace(/I/g, '9')
      .replace(/=/g, '')
  } catch (e) {
    return null
  }
}
