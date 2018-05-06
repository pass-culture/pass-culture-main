/** Queries available disk quota.
  @see https://developer.mozilla.org/en-US/docs/Web/API/StorageEstimate
  @returns {Promise<{quota: number, usage: number}>} Promise resolved with
  {quota: number, usage: number} or undefined.
*/
export async function showEstimatedQuota() {
  /*
  navigator.webkitPersistentStorage.queryUsageAndQuota (
      function(usedBytes, grantedBytes) {
          console.log('we are using ', usedBytes, ' of ', grantedBytes, 'bytes');
      },
      function(e) { console.log('Error', e);  }
  );

  var requestedBytes = 1024*1024*280;

  navigator.webkitPersistentStorage.requestQuota (
      requestedBytes, function(grantedBytes) {
          console.log('we were granted ', grantedBytes, 'bytes');

      }, function(e) { console.log('Error', e); }
  );
  */
  /*
  return await navigator.storage && navigator.storage.estimate ?
    navigator.storage.estimate() :
    undefined;
  */
}
