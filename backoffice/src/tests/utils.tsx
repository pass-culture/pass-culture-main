import flushPromises from 'flush-promises'
import { act } from '@testing-library/react'

export async function flushAllPromises() {
  await flushPromises()
  return new Promise(setImmediate)
}

export async function flushAllPromisesTimes(times: number) {
  for (let i = 0; i < times; i++) {
    await flushAllPromises()
  }
}

export async function superFlushWithAct(times = 50) {
  await act(async () => {
    await flushAllPromisesTimes(times)
  })
}
