/**
 * Runs `worker(item)` over `items` with a bounded number of concurrent
 * promises. Preserves input order in the resulting array.
 */
export async function runWithConcurrency(items, worker, concurrency) {
  const results = new Array(items.length)
  let cursor = 0
  async function pull() {
    while (cursor < items.length) {
      const index = cursor
      cursor += 1
      results[index] = await worker(items[index])
    }
  }
  const workerCount = Math.max(1, Math.min(concurrency, items.length))
  await Promise.all(Array.from({ length: workerCount }, pull))
  return results
}
