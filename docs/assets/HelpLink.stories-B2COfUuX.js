var et=(t,e,r)=>{if(!e.has(t))throw TypeError("Cannot "+r)};var u=(t,e,r)=>(et(t,e,"read from private field"),r?r.call(t):e.get(t)),g=(t,e,r)=>{if(e.has(t))throw TypeError("Cannot add the same private member more than once");e instanceof WeakSet?e.add(t):e.set(t,r)},h=(t,e,r,s)=>(et(t,e,"write to private field"),s?s.call(t,r):e.set(t,r),r);import{j as re}from"./jsx-runtime-X2b_N9AH.js";import{r as pr}from"./index-uCp2LrAq.js";import{U as Be,A as qt}from"./config-CMzMHASz.js";import"./VenuePhysicalLocation-BNqBgyMK.js";import{u as fr}from"./index-DoMt6nTV.js";import{f as mr}from"./full-help-Co3hxUDJ.js";import{S as br}from"./SvgIcon-DP_815J1.js";import"./_commonjsHelpers-BosuxZz1.js";let gr=class{constructor(e){this.config=e}},ve=class extends Error{constructor(e,r,s){super(s),this.name="ApiError",this.url=r.url,this.status=r.status,this.statusText=r.statusText,this.body=r.body,this.request=e}},Er=class extends Error{constructor(e){super(e),this.name="CancelError"}get isCancelled(){return!0}};var q,w,R,N,V,Q,U,_t;let yr=(_t=class{constructor(e){g(this,q,void 0);g(this,w,void 0);g(this,R,void 0);g(this,N,void 0);g(this,V,void 0);g(this,Q,void 0);g(this,U,void 0);h(this,q,!1),h(this,w,!1),h(this,R,!1),h(this,N,[]),h(this,V,new Promise((r,s)=>{h(this,Q,r),h(this,U,s);const n=a=>{u(this,q)||u(this,w)||u(this,R)||(h(this,q,!0),u(this,Q)&&u(this,Q).call(this,a))},o=a=>{u(this,q)||u(this,w)||u(this,R)||(h(this,w,!0),u(this,U)&&u(this,U).call(this,a))},i=a=>{u(this,q)||u(this,w)||u(this,R)||u(this,N).push(a)};return Object.defineProperty(i,"isResolved",{get:()=>u(this,q)}),Object.defineProperty(i,"isRejected",{get:()=>u(this,w)}),Object.defineProperty(i,"isCancelled",{get:()=>u(this,R)}),e(n,o,i)}))}get[Symbol.toStringTag](){return"Cancellable Promise"}then(e,r){return u(this,V).then(e,r)}catch(e){return u(this,V).catch(e)}finally(e){return u(this,V).finally(e)}cancel(){if(!(u(this,q)||u(this,w)||u(this,R))){if(h(this,R,!0),u(this,N).length)try{for(const e of u(this,N))e()}catch(e){console.warn("Cancellation threw an error",e);return}u(this,N).length=0,u(this,U)&&u(this,U).call(this,new Er("Request aborted"))}}get isCancelled(){return u(this,R)}},q=new WeakMap,w=new WeakMap,R=new WeakMap,N=new WeakMap,V=new WeakMap,Q=new WeakMap,U=new WeakMap,_t);const $e=t=>t!=null,ie=t=>typeof t=="string",Ee=t=>ie(t)&&t!=="",Me=t=>typeof t=="object"&&typeof t.type=="string"&&typeof t.stream=="function"&&typeof t.arrayBuffer=="function"&&typeof t.constructor=="function"&&typeof t.constructor.name=="string"&&/^(Blob|File)$/.test(t.constructor.name)&&/^(Blob|File)$/.test(t[Symbol.toStringTag]),wt=t=>t instanceof FormData,Tr=t=>{try{return btoa(t)}catch{return Buffer.from(t).toString("base64")}},_r=t=>{const e=[],r=(n,o)=>{e.push(`${encodeURIComponent(n)}=${encodeURIComponent(String(o))}`)},s=(n,o)=>{$e(o)&&(Array.isArray(o)?o.forEach(i=>{s(n,i)}):typeof o=="object"?Object.entries(o).forEach(([i,a])=>{s(`${n}[${i}]`,a)}):r(n,o))};return Object.entries(t).forEach(([n,o])=>{s(n,o)}),e.length>0?`?${e.join("&")}`:""},Cr=(t,e)=>{const r=t.ENCODE_PATH||encodeURI,s=e.url.replace("{api-version}",t.VERSION).replace(/{(.*?)}/g,(o,i)=>{var a;return(a=e.path)!=null&&a.hasOwnProperty(i)?r(String(e.path[i])):o}),n=`${t.BASE}${s}`;return e.query?`${n}${_r(e.query)}`:n},Rr=t=>{if(t.formData){const e=new FormData,r=(s,n)=>{ie(n)||Me(n)?e.append(s,n):e.append(s,JSON.stringify(n))};return Object.entries(t.formData).filter(([s,n])=>$e(n)).forEach(([s,n])=>{Array.isArray(n)?n.forEach(o=>r(s,o)):r(s,n)}),e}},le=async(t,e)=>typeof e=="function"?e(t):e,Sr=async(t,e)=>{const r=await le(e,t.TOKEN),s=await le(e,t.USERNAME),n=await le(e,t.PASSWORD),o=await le(e,t.HEADERS),i=Object.entries({Accept:"application/json",...o,...e.headers}).filter(([a,c])=>$e(c)).reduce((a,[c,l])=>({...a,[c]:String(l)}),{});if(Ee(r)&&(i.Authorization=`Bearer ${r}`),Ee(s)&&Ee(n)){const a=Tr(`${s}:${n}`);i.Authorization=`Basic ${a}`}return e.body&&(e.mediaType?i["Content-Type"]=e.mediaType:Me(e.body)?i["Content-Type"]=e.body.type||"application/octet-stream":ie(e.body)?i["Content-Type"]="text/plain":wt(e.body)||(i["Content-Type"]="application/json")),new Headers(i)},Ir=t=>{var e;if(t.body)return(e=t.mediaType)!=null&&e.includes("/json")?JSON.stringify(t.body):ie(t.body)||Me(t.body)||wt(t.body)?t.body:JSON.stringify(t.body)},qr=(t,e,r,s,n,o,i)=>{const a=new AbortController,c={headers:o,body:s??n,method:e.method,signal:a.signal};return t.WITH_CREDENTIALS&&(c.credentials=t.CREDENTIALS),i(()=>a.abort()),fetch(r,c)},wr=(t,e)=>{if(e){const r=t.headers.get(e);if(ie(r))return r}},Ar=async t=>{if(t.status!==204)try{const e=t.headers.get("Content-Type");if(e){const r=e.toLowerCase(),s=r.startsWith("application/json"),n=["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","application/vnd.ms-excel","text/csv"].some(o=>r.includes(o));return s?await t.json():n?await t.blob():await t.text()}}catch(e){console.error(e)}},vr=(t,e)=>{const s={400:"Bad Request",401:"Unauthorized",403:"Forbidden",404:"Not Found",500:"Internal Server Error",502:"Bad Gateway",503:"Service Unavailable",...t.errors}[e.status];if(e.status===503){window.location.assign(Be);return}if(s)throw new ve(t,e,s);if(!e.ok)throw new ve(t,e,"Generic Error")},Or=(t,e)=>new yr(async(r,s,n)=>{try{const o=Cr(t,e),i=Rr(e),a=Ir(e),c=await Sr(t,e);if(!n.isCancelled){const l=await qr(t,e,o,a,i,c,n),d=await Ar(l),p=wr(l,e.responseHeader),f={url:o,ok:l.ok,status:l.status,statusText:l.statusText,body:p??d};vr(e,f),r(f.body)}}catch(o){if(o instanceof ve&&o.status===401){if(o.url.includes("/adage-iframe")){window.location.href="/adage-iframe/erreur";return}if(!o.url.includes("/users/current")&&!o.url.includes("/users/signin")){window.location.href="/connexion";return}}s(o)}});let Fr=class extends gr{constructor(e){super(e)}request(e){return Or(this.config,e)}},Dr=class{constructor(e){this.httpRequest=e}getBookingsCsv(e=1,r,s,n,o,i,a,c,l){return this.httpRequest.request({method:"GET",url:"/bookings/csv",query:{page:e,venueId:r,offerId:s,eventDate:n,bookingStatusFilter:o,bookingPeriodBeginningDate:i,bookingPeriodEndingDate:a,offerType:c,exportType:l},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getOfferPriceCategoriesAndSchedulesByDates(e){return this.httpRequest.request({method:"GET",url:"/bookings/dates/{offer_id}",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getBookingsExcel(e=1,r,s,n,o,i,a,c,l){return this.httpRequest.request({method:"GET",url:"/bookings/excel",query:{page:e,venueId:r,offerId:s,eventDate:n,bookingStatusFilter:o,bookingPeriodBeginningDate:i,bookingPeriodEndingDate:a,offerType:c,exportType:l},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}exportBookingsForOfferAsCsv(e,r,s){return this.httpRequest.request({method:"GET",url:"/bookings/offer/{offer_id}/csv",path:{offer_id:e},query:{status:r,event_date:s},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}exportBookingsForOfferAsExcel(e,r,s){return this.httpRequest.request({method:"GET",url:"/bookings/offer/{offer_id}/excel",path:{offer_id:e},query:{status:r,event_date:s},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getBookingsPro(e=1,r,s,n,o,i,a,c,l){return this.httpRequest.request({method:"GET",url:"/bookings/pro",query:{page:e,venueId:r,offerId:s,eventDate:n,bookingStatusFilter:o,bookingPeriodBeginningDate:i,bookingPeriodEndingDate:a,offerType:c,exportType:l},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getUserHasBookings(){return this.httpRequest.request({method:"GET",url:"/bookings/pro/userHasBookings",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveBookingsCsv(e=1,r,s,n,o,i){return this.httpRequest.request({method:"GET",url:"/collective/bookings/csv",query:{page:e,venueId:r,eventDate:s,bookingStatusFilter:n,bookingPeriodBeginningDate:o,bookingPeriodEndingDate:i},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveBookingsExcel(e=1,r,s,n,o,i){return this.httpRequest.request({method:"GET",url:"/collective/bookings/excel",query:{page:e,venueId:r,eventDate:s,bookingStatusFilter:n,bookingPeriodBeginningDate:o,bookingPeriodEndingDate:i},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveBookingsPro(e=1,r,s,n,o,i){return this.httpRequest.request({method:"GET",url:"/collective/bookings/pro",query:{page:e,venueId:r,eventDate:s,bookingStatusFilter:n,bookingPeriodBeginningDate:o,bookingPeriodEndingDate:i},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getUserHasCollectiveBookings(){return this.httpRequest.request({method:"GET",url:"/collective/bookings/pro/userHasBookings",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveBookingById(e){return this.httpRequest.request({method:"GET",url:"/collective/bookings/{booking_id}",path:{booking_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}listEducationalDomains(){return this.httpRequest.request({method:"GET",url:"/collective/educational-domains",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveOffers(e,r,s,n,o,i,a,c,l,d){return this.httpRequest.request({method:"GET",url:"/collective/offers",query:{nameOrIsbn:e,offererId:r,status:s,venueId:n,categoryId:o,creationMode:i,periodBeginningDate:a,periodEndingDate:c,collectiveOfferType:l,format:d},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}createCollectiveOffer(e){return this.httpRequest.request({method:"POST",url:"/collective/offers",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}createCollectiveOfferTemplate(e){return this.httpRequest.request({method:"POST",url:"/collective/offers-template",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchCollectiveOffersTemplateActiveStatus(e){return this.httpRequest.request({method:"PATCH",url:"/collective/offers-template/active-status",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveOfferRequest(e){return this.httpRequest.request({method:"GET",url:"/collective/offers-template/request/{request_id}",path:{request_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveOfferTemplate(e){return this.httpRequest.request({method:"GET",url:"/collective/offers-template/{offer_id}",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}editCollectiveOfferTemplate(e,r){return this.httpRequest.request({method:"PATCH",url:"/collective/offers-template/{offer_id}",path:{offer_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}createCollectiveOfferTemplateFromCollectiveOffer(e,r){return this.httpRequest.request({method:"POST",url:"/collective/offers-template/{offer_id}/",path:{offer_id:e},body:r,mediaType:"application/json",errors:{400:"Bad Request",403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}deleteOfferTemplateImage(e){return this.httpRequest.request({method:"DELETE",url:"/collective/offers-template/{offer_id}/image",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}attachOfferTemplateImage(e,r){return this.httpRequest.request({method:"POST",url:"/collective/offers-template/{offer_id}/image",path:{offer_id:e},formData:r,mediaType:"multipart/form-data",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchCollectiveOfferTemplatePublication(e){return this.httpRequest.request({method:"PATCH",url:"/collective/offers-template/{offer_id}/publish",path:{offer_id:e},errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}patchCollectiveOffersActiveStatus(e){return this.httpRequest.request({method:"PATCH",url:"/collective/offers/active-status",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchAllCollectiveOffersActiveStatus(e){return this.httpRequest.request({method:"PATCH",url:"/collective/offers/all-active-status",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getAutocompleteEducationalRedactorsForUai(e,r){return this.httpRequest.request({method:"GET",url:"/collective/offers/redactors",query:{uai:e,candidate:r},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveOffer(e){return this.httpRequest.request({method:"GET",url:"/collective/offers/{offer_id}",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}editCollectiveOffer(e,r){return this.httpRequest.request({method:"PATCH",url:"/collective/offers/{offer_id}",path:{offer_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}cancelCollectiveOfferBooking(e){return this.httpRequest.request({method:"PATCH",url:"/collective/offers/{offer_id}/cancel_booking",path:{offer_id:e},errors:{400:"Bad Request",403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}duplicateCollectiveOffer(e){return this.httpRequest.request({method:"POST",url:"/collective/offers/{offer_id}/duplicate",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchCollectiveOffersEducationalInstitution(e,r){return this.httpRequest.request({method:"PATCH",url:"/collective/offers/{offer_id}/educational_institution",path:{offer_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}deleteOfferImage(e){return this.httpRequest.request({method:"DELETE",url:"/collective/offers/{offer_id}/image",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}attachOfferImage(e,r){return this.httpRequest.request({method:"POST",url:"/collective/offers/{offer_id}/image",path:{offer_id:e},formData:r,mediaType:"multipart/form-data",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchCollectiveOfferPublication(e){return this.httpRequest.request({method:"PATCH",url:"/collective/offers/{offer_id}/publish",path:{offer_id:e},errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}createCollectiveStock(e){return this.httpRequest.request({method:"POST",url:"/collective/stocks",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}editCollectiveStock(e,r){return this.httpRequest.request({method:"PATCH",url:"/collective/stocks/{collective_stock_id}",path:{collective_stock_id:e},body:r,mediaType:"application/json",errors:{400:"Bad Request",401:"Unauthorized",403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}getEducationalPartners(){return this.httpRequest.request({method:"GET",url:"/cultural-partners",errors:{401:"Unauthorized",403:"Forbidden",422:"Unprocessable Entity"}})}getEducationalInstitutions(e=1e3,r=1){return this.httpRequest.request({method:"GET",url:"/educational_institutions",query:{perPageLimit:e,page:r},errors:{401:"Unauthorized",403:"Forbidden",422:"Unprocessable Entity"}})}listFeatures(){return this.httpRequest.request({method:"GET",url:"/features",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getBankAccounts(){return this.httpRequest.request({method:"GET",url:"/finance/bank-accounts",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getNationalPrograms(){return this.httpRequest.request({method:"GET",url:"/national-programs",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}createOfferer(e){return this.httpRequest.request({method:"POST",url:"/offerers",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}deleteApiKey(e){return this.httpRequest.request({method:"DELETE",url:"/offerers/api_keys/{api_key_prefix}",path:{api_key_prefix:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}listEducationalOfferers(e){return this.httpRequest.request({method:"GET",url:"/offerers/educational",query:{offerer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}listOfferersNames(e,r,s){return this.httpRequest.request({method:"GET",url:"/offerers/names",query:{validated:e,validated_for_user:r,offerer_id:s},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}saveNewOnboardingData(e){return this.httpRequest.request({method:"POST",url:"/offerers/new",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getOfferer(e){return this.httpRequest.request({method:"GET",url:"/offerers/{offerer_id}",path:{offerer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchOffererAddress(e,r,s){return this.httpRequest.request({method:"PATCH",url:"/offerers/{offerer_id}/address/{offerer_address_id}",path:{offerer_id:e,offerer_address_id:r},body:s,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getOffererAddresses(e){return this.httpRequest.request({method:"GET",url:"/offerers/{offerer_id}/addresses",path:{offerer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}createOffererAddress(e,r){return this.httpRequest.request({method:"POST",url:"/offerers/{offerer_id}/addresses",path:{offerer_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}generateApiKeyRoute(e){return this.httpRequest.request({method:"POST",url:"/offerers/{offerer_id}/api_keys",path:{offerer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getOffererBankAccountsAndAttachedVenues(e){return this.httpRequest.request({method:"GET",url:"/offerers/{offerer_id}/bank-accounts",path:{offerer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}linkVenueToBankAccount(e,r,s){return this.httpRequest.request({method:"PATCH",url:"/offerers/{offerer_id}/bank-accounts/{bank_account_id}",path:{offerer_id:e,bank_account_id:r},body:s,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getOffererStatsDashboardUrl(e){return this.httpRequest.request({method:"GET",url:"/offerers/{offerer_id}/dashboard",path:{offerer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}inviteMember(e,r){return this.httpRequest.request({method:"POST",url:"/offerers/{offerer_id}/invite",path:{offerer_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getOffererMembers(e){return this.httpRequest.request({method:"GET",url:"/offerers/{offerer_id}/members",path:{offerer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getOffererStats(e){return this.httpRequest.request({method:"GET",url:"/offerers/{offerer_id}/stats",path:{offerer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getOffererV2Stats(e){return this.httpRequest.request({method:"GET",url:"/offerers/{offerer_id}/v2/stats",path:{offerer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}listOffers(e,r,s,n,o,i,a,c,l){return this.httpRequest.request({method:"GET",url:"/offers",query:{nameOrIsbn:e,offererId:r,status:s,venueId:n,categoryId:o,creationMode:i,periodBeginningDate:a,periodEndingDate:c,collectiveOfferType:l},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}postOffer(e){return this.httpRequest.request({method:"POST",url:"/offers",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchOffersActiveStatus(e){return this.httpRequest.request({method:"PATCH",url:"/offers/active-status",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchAllOffersActiveStatus(e){return this.httpRequest.request({method:"PATCH",url:"/offers/all-active-status",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCategories(){return this.httpRequest.request({method:"GET",url:"/offers/categories",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}deleteDraftOffers(e){return this.httpRequest.request({method:"POST",url:"/offers/delete-draft",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getMusicTypes(){return this.httpRequest.request({method:"GET",url:"/offers/music-types",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchPublishOffer(e){return this.httpRequest.request({method:"PATCH",url:"/offers/publish",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}createThumbnail(e){return this.httpRequest.request({method:"POST",url:"/offers/thumbnails/",formData:e,mediaType:"multipart/form-data",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}deleteThumbnail(e){return this.httpRequest.request({method:"DELETE",url:"/offers/thumbnails/{offer_id}",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getOffer(e){return this.httpRequest.request({method:"GET",url:"/offers/{offer_id}",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchOffer(e,r){return this.httpRequest.request({method:"PATCH",url:"/offers/{offer_id}",path:{offer_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}postPriceCategories(e,r){return this.httpRequest.request({method:"POST",url:"/offers/{offer_id}/price_categories",path:{offer_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}deletePriceCategory(e,r){return this.httpRequest.request({method:"DELETE",url:"/offers/{offer_id}/price_categories/{price_category_id}",path:{offer_id:e,price_category_id:r},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getStocksStats(e){return this.httpRequest.request({method:"GET",url:"/offers/{offer_id}/stocks-stats",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getStocks(e,r,s,n,o,i=!1,a=1,c=20){return this.httpRequest.request({method:"GET",url:"/offers/{offer_id}/stocks/",path:{offer_id:e},query:{date:r,time:s,price_category_id:n,order_by:o,order_by_desc:i,page:a,stocks_limit_per_page:c},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}deleteAllFilteredStocks(e,r){return this.httpRequest.request({method:"POST",url:"/offers/{offer_id}/stocks/all-delete",path:{offer_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}deleteStocks(e,r){return this.httpRequest.request({method:"POST",url:"/offers/{offer_id}/stocks/delete",path:{offer_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getReimbursementsCsv(e,r,s){return this.httpRequest.request({method:"GET",url:"/reimbursements/csv",query:{venueId:e,reimbursementPeriodBeginningDate:r,reimbursementPeriodEndingDate:s},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getSirenInfo(e){return this.httpRequest.request({method:"GET",url:"/sirene/siren/{siren}",path:{siren:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getSiretInfo(e){return this.httpRequest.request({method:"GET",url:"/sirene/siret/{siret}",path:{siret:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}upsertStocks(e){return this.httpRequest.request({method:"POST",url:"/stocks/bulk",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}deleteStock(e){return this.httpRequest.request({method:"DELETE",url:"/stocks/{stock_id}",path:{stock_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}connectAs(e){return this.httpRequest.request({method:"GET",url:"/users/connect-as/{token}",path:{token:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}cookiesConsent(e){return this.httpRequest.request({method:"POST",url:"/users/cookies",body:e,mediaType:"application/json",errors:{400:"Bad Request",403:"Forbidden",422:"Unprocessable Entity"}})}getProfile(){return this.httpRequest.request({method:"GET",url:"/users/current",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}postUserEmail(e){return this.httpRequest.request({method:"POST",url:"/users/email",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getUserEmailPendingValidation(){return this.httpRequest.request({method:"GET",url:"/users/email_pending_validation",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchUserIdentity(e){return this.httpRequest.request({method:"PATCH",url:"/users/identity",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}submitNewNavReview(e){return this.httpRequest.request({method:"POST",url:"/users/log-new-nav-review",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}postNewPassword(e){return this.httpRequest.request({method:"POST",url:"/users/new-password",body:e,mediaType:"application/json",errors:{400:"Bad Request",403:"Forbidden",422:"Unprocessable Entity"}})}postNewProNav(){return this.httpRequest.request({method:"POST",url:"/users/new-pro-nav",errors:{400:"Bad Request",403:"Forbidden",422:"Unprocessable Entity"}})}postChangePassword(e){return this.httpRequest.request({method:"POST",url:"/users/password",body:e,mediaType:"application/json",errors:{400:"Bad Request",403:"Forbidden",422:"Unprocessable Entity"}})}patchUserPhone(e){return this.httpRequest.request({method:"PATCH",url:"/users/phone",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}postProFlags(e){return this.httpRequest.request({method:"POST",url:"/users/pro_flags",body:e,mediaType:"application/json",errors:{400:"Bad Request",403:"Forbidden",422:"Unprocessable Entity"}})}resetPassword(e){return this.httpRequest.request({method:"POST",url:"/users/reset-password",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchProUserRgsSeen(){return this.httpRequest.request({method:"PATCH",url:"/users/rgs-seen",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}signin(e){return this.httpRequest.request({method:"POST",url:"/users/signin",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}signout(){return this.httpRequest.request({method:"GET",url:"/users/signout",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}checkActivationTokenExists(e){return this.httpRequest.request({method:"GET",url:"/users/token/{token}",path:{token:e},errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}patchUserTutoSeen(){return this.httpRequest.request({method:"PATCH",url:"/users/tuto-seen",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}patchValidateEmail(e){return this.httpRequest.request({method:"PATCH",url:"/users/validate_email",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}hasInvoice(e){return this.httpRequest.request({method:"GET",url:"/v2/finance/has-invoice",query:{offererId:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getInvoicesV2(e,r,s,n){return this.httpRequest.request({method:"GET",url:"/v2/finance/invoices",query:{periodBeginningDate:e,periodEndingDate:r,bankAccountId:s,offererId:n},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}signupProV2(e){return this.httpRequest.request({method:"POST",url:"/v2/users/signup/pro",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}validateUser(e){return this.httpRequest.request({method:"PATCH",url:"/validate/user/{token}",path:{token:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}fetchVenueLabels(){return this.httpRequest.request({method:"GET",url:"/venue-labels",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getVenueTypes(){return this.httpRequest.request({method:"GET",url:"/venue-types",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}listVenueProviders(e){return this.httpRequest.request({method:"GET",url:"/venueProviders",query:{venueId:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}createVenueProvider(e){return this.httpRequest.request({method:"POST",url:"/venueProviders",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}updateVenueProvider(e){return this.httpRequest.request({method:"PUT",url:"/venueProviders",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getProvidersByVenue(e){return this.httpRequest.request({method:"GET",url:"/venueProviders/{venue_id}",path:{venue_id:e},errors:{401:"Unauthorized",403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}deleteVenueProvider(e){return this.httpRequest.request({method:"DELETE",url:"/venueProviders/{venue_provider_id}",path:{venue_provider_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getVenues(e,r,s){return this.httpRequest.request({method:"GET",url:"/venues",query:{validated:e,activeOfferersOnly:r,offererId:s},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}postCreateVenue(e){return this.httpRequest.request({method:"POST",url:"/venues",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getVenuesEducationalStatuses(){return this.httpRequest.request({method:"GET",url:"/venues-educational-statuses",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getVenuesOfOffererFromSiret(e){return this.httpRequest.request({method:"GET",url:"/venues/siret/{siret}",path:{siret:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getVenue(e){return this.httpRequest.request({method:"GET",url:"/venues/{venue_id}",path:{venue_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}editVenue(e,r){return this.httpRequest.request({method:"PATCH",url:"/venues/{venue_id}",path:{venue_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}deleteVenueBanner(e){return this.httpRequest.request({method:"DELETE",url:"/venues/{venue_id}/banner",path:{venue_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}editVenueCollectiveData(e,r){return this.httpRequest.request({method:"PATCH",url:"/venues/{venue_id}/collective-data",path:{venue_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getVenueStatsDashboardUrl(e){return this.httpRequest.request({method:"GET",url:"/venues/{venue_id}/dashboard",path:{venue_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}linkVenueToPricingPoint(e,r){return this.httpRequest.request({method:"POST",url:"/venues/{venue_id}/pricing-point",path:{venue_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getVenueStats(e){return this.httpRequest.request({method:"GET",url:"/venues/{venue_id}/stats",path:{venue_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}};class Pr{constructor(e,r=Fr){this.request=new r({BASE:(e==null?void 0:e.BASE)??"http://localhost:5001",VERSION:(e==null?void 0:e.VERSION)??"1",WITH_CREDENTIALS:(e==null?void 0:e.WITH_CREDENTIALS)??!1,CREDENTIALS:(e==null?void 0:e.CREDENTIALS)??"include",TOKEN:e==null?void 0:e.TOKEN,USERNAME:e==null?void 0:e.USERNAME,PASSWORD:e==null?void 0:e.PASSWORD,HEADERS:e==null?void 0:e.HEADERS,ENCODE_PATH:e==null?void 0:e.ENCODE_PATH}),this.default=new Dr(this.request)}}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const At=function(t){const e=[];let r=0;for(let s=0;s<t.length;s++){let n=t.charCodeAt(s);n<128?e[r++]=n:n<2048?(e[r++]=n>>6|192,e[r++]=n&63|128):(n&64512)===55296&&s+1<t.length&&(t.charCodeAt(s+1)&64512)===56320?(n=65536+((n&1023)<<10)+(t.charCodeAt(++s)&1023),e[r++]=n>>18|240,e[r++]=n>>12&63|128,e[r++]=n>>6&63|128,e[r++]=n&63|128):(e[r++]=n>>12|224,e[r++]=n>>6&63|128,e[r++]=n&63|128)}return e},kr=function(t){const e=[];let r=0,s=0;for(;r<t.length;){const n=t[r++];if(n<128)e[s++]=String.fromCharCode(n);else if(n>191&&n<224){const o=t[r++];e[s++]=String.fromCharCode((n&31)<<6|o&63)}else if(n>239&&n<365){const o=t[r++],i=t[r++],a=t[r++],c=((n&7)<<18|(o&63)<<12|(i&63)<<6|a&63)-65536;e[s++]=String.fromCharCode(55296+(c>>10)),e[s++]=String.fromCharCode(56320+(c&1023))}else{const o=t[r++],i=t[r++];e[s++]=String.fromCharCode((n&15)<<12|(o&63)<<6|i&63)}}return e.join("")},Nr={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(t,e){if(!Array.isArray(t))throw Error("encodeByteArray takes an array as a parameter");this.init_();const r=e?this.byteToCharMapWebSafe_:this.byteToCharMap_,s=[];for(let n=0;n<t.length;n+=3){const o=t[n],i=n+1<t.length,a=i?t[n+1]:0,c=n+2<t.length,l=c?t[n+2]:0,d=o>>2,p=(o&3)<<4|a>>4;let f=(a&15)<<2|l>>6,E=l&63;c||(E=64,i||(f=64)),s.push(r[d],r[p],r[f],r[E])}return s.join("")},encodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?btoa(t):this.encodeByteArray(At(t),e)},decodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?atob(t):kr(this.decodeStringToByteArray(t,e))},decodeStringToByteArray(t,e){this.init_();const r=e?this.charToByteMapWebSafe_:this.charToByteMap_,s=[];for(let n=0;n<t.length;){const o=r[t.charAt(n++)],a=n<t.length?r[t.charAt(n)]:0;++n;const l=n<t.length?r[t.charAt(n)]:64;++n;const p=n<t.length?r[t.charAt(n)]:64;if(++n,o==null||a==null||l==null||p==null)throw new Ur;const f=o<<2|a>>4;if(s.push(f),l!==64){const E=a<<4&240|l>>2;if(s.push(E),p!==64){const P=l<<6&192|p;s.push(P)}}}return s},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let t=0;t<this.ENCODED_VALS.length;t++)this.byteToCharMap_[t]=this.ENCODED_VALS.charAt(t),this.charToByteMap_[this.byteToCharMap_[t]]=t,this.byteToCharMapWebSafe_[t]=this.ENCODED_VALS_WEBSAFE.charAt(t),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[t]]=t,t>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(t)]=t,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(t)]=t)}}};class Ur extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const Lr=function(t){const e=At(t);return Nr.encodeByteArray(e,!0)},vt=function(t){return Lr(t).replace(/\./g,"")};function Br(){try{return typeof indexedDB=="object"}catch{return!1}}function $r(){return new Promise((t,e)=>{try{let r=!0;const s="validate-browser-context-for-indexeddb-analytics-module",n=self.indexedDB.open(s);n.onsuccess=()=>{n.result.close(),r||self.indexedDB.deleteDatabase(s),t(!0)},n.onupgradeneeded=()=>{r=!1},n.onerror=()=>{var o;e(((o=n.error)===null||o===void 0?void 0:o.message)||"")}}catch(r){e(r)}})}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Mr="FirebaseError";let He=class Ot extends Error{constructor(e,r,s){super(r),this.code=e,this.customData=s,this.name=Mr,Object.setPrototypeOf(this,Ot.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,Ft.prototype.create)}},Ft=class{constructor(e,r,s){this.service=e,this.serviceName=r,this.errors=s}create(e,...r){const s=r[0]||{},n=`${this.service}/${e}`,o=this.errors[e],i=o?Hr(o,s):"Error",a=`${this.serviceName}: ${i} (${n}).`;return new He(n,a,s)}};function Hr(t,e){return t.replace(jr,(r,s)=>{const n=e[s];return n!=null?String(n):`<${s}?>`})}const jr=/\{\$([^}]+)}/g;let Oe=class{constructor(e,r,s){this.name=e,this.instanceFactory=r,this.type=s,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}};/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */var b;(function(t){t[t.DEBUG=0]="DEBUG",t[t.VERBOSE=1]="VERBOSE",t[t.INFO=2]="INFO",t[t.WARN=3]="WARN",t[t.ERROR=4]="ERROR",t[t.SILENT=5]="SILENT"})(b||(b={}));const xr={debug:b.DEBUG,verbose:b.VERBOSE,info:b.INFO,warn:b.WARN,error:b.ERROR,silent:b.SILENT},Gr=b.INFO,Vr={[b.DEBUG]:"log",[b.VERBOSE]:"log",[b.INFO]:"info",[b.WARN]:"warn",[b.ERROR]:"error"},Kr=(t,e,...r)=>{if(e<t.logLevel)return;const s=new Date().toISOString(),n=Vr[e];if(n)console[n](`[${s}]  ${t.name}:`,...r);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};let Wr=class{constructor(e){this.name=e,this._logLevel=Gr,this._logHandler=Kr,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in b))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?xr[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,b.DEBUG,...e),this._logHandler(this,b.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,b.VERBOSE,...e),this._logHandler(this,b.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,b.INFO,...e),this._logHandler(this,b.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,b.WARN,...e),this._logHandler(this,b.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,b.ERROR,...e),this._logHandler(this,b.ERROR,...e)}};const zr=(t,e)=>e.some(r=>t instanceof r);let tt,rt;function Jr(){return tt||(tt=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Yr(){return rt||(rt=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Dt=new WeakMap,Fe=new WeakMap,Pt=new WeakMap,ye=new WeakMap,je=new WeakMap;function Qr(t){const e=new Promise((r,s)=>{const n=()=>{t.removeEventListener("success",o),t.removeEventListener("error",i)},o=()=>{r(H(t.result)),n()},i=()=>{s(t.error),n()};t.addEventListener("success",o),t.addEventListener("error",i)});return e.then(r=>{r instanceof IDBCursor&&Dt.set(r,t)}).catch(()=>{}),je.set(e,t),e}function Xr(t){if(Fe.has(t))return;const e=new Promise((r,s)=>{const n=()=>{t.removeEventListener("complete",o),t.removeEventListener("error",i),t.removeEventListener("abort",i)},o=()=>{r(),n()},i=()=>{s(t.error||new DOMException("AbortError","AbortError")),n()};t.addEventListener("complete",o),t.addEventListener("error",i),t.addEventListener("abort",i)});Fe.set(t,e)}let De={get(t,e,r){if(t instanceof IDBTransaction){if(e==="done")return Fe.get(t);if(e==="objectStoreNames")return t.objectStoreNames||Pt.get(t);if(e==="store")return r.objectStoreNames[1]?void 0:r.objectStore(r.objectStoreNames[0])}return H(t[e])},set(t,e,r){return t[e]=r,!0},has(t,e){return t instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in t}};function Zr(t){De=t(De)}function es(t){return t===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...r){const s=t.call(Te(this),e,...r);return Pt.set(s,e.sort?e.sort():[e]),H(s)}:Yr().includes(t)?function(...e){return t.apply(Te(this),e),H(Dt.get(this))}:function(...e){return H(t.apply(Te(this),e))}}function ts(t){return typeof t=="function"?es(t):(t instanceof IDBTransaction&&Xr(t),zr(t,Jr())?new Proxy(t,De):t)}function H(t){if(t instanceof IDBRequest)return Qr(t);if(ye.has(t))return ye.get(t);const e=ts(t);return e!==t&&(ye.set(t,e),je.set(e,t)),e}const Te=t=>je.get(t);function kt(t,e,{blocked:r,upgrade:s,blocking:n,terminated:o}={}){const i=indexedDB.open(t,e),a=H(i);return s&&i.addEventListener("upgradeneeded",c=>{s(H(i.result),c.oldVersion,c.newVersion,H(i.transaction),c)}),r&&i.addEventListener("blocked",c=>r(c.oldVersion,c.newVersion,c)),a.then(c=>{o&&c.addEventListener("close",()=>o()),n&&c.addEventListener("versionchange",l=>n(l.oldVersion,l.newVersion,l))}).catch(()=>{}),a}const rs=["get","getKey","getAll","getAllKeys","count"],ss=["put","add","delete","clear"],_e=new Map;function st(t,e){if(!(t instanceof IDBDatabase&&!(e in t)&&typeof e=="string"))return;if(_e.get(e))return _e.get(e);const r=e.replace(/FromIndex$/,""),s=e!==r,n=ss.includes(r);if(!(r in(s?IDBIndex:IDBObjectStore).prototype)||!(n||rs.includes(r)))return;const o=async function(i,...a){const c=this.transaction(i,n?"readwrite":"readonly");let l=c.store;return s&&(l=l.index(a.shift())),(await Promise.all([l[r](...a),n&&c.done]))[0]};return _e.set(e,o),o}Zr(t=>({...t,get:(e,r,s)=>st(e,r)||t.get(e,r,s),has:(e,r)=>!!st(e,r)||t.has(e,r)}));/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class ns{constructor(e){this.container=e}getPlatformInfoString(){return this.container.getProviders().map(r=>{if(os(r)){const s=r.getImmediate();return`${s.library}/${s.version}`}else return null}).filter(r=>r).join(" ")}}function os(t){const e=t.getComponent();return(e==null?void 0:e.type)==="VERSION"}const Pe="@firebase/app",nt="0.10.2";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const z=new Wr("@firebase/app"),is="@firebase/app-compat",as="@firebase/analytics-compat",cs="@firebase/analytics",ls="@firebase/app-check-compat",us="@firebase/app-check",ds="@firebase/auth",hs="@firebase/auth-compat",ps="@firebase/database",fs="@firebase/database-compat",ms="@firebase/functions",bs="@firebase/functions-compat",gs="@firebase/installations",Es="@firebase/installations-compat",ys="@firebase/messaging",Ts="@firebase/messaging-compat",_s="@firebase/performance",Cs="@firebase/performance-compat",Rs="@firebase/remote-config",Ss="@firebase/remote-config-compat",Is="@firebase/storage",qs="@firebase/storage-compat",ws="@firebase/firestore",As="@firebase/firestore-compat",vs="firebase",Os="10.11.1",Fs={[Pe]:"fire-core",[is]:"fire-core-compat",[cs]:"fire-analytics",[as]:"fire-analytics-compat",[us]:"fire-app-check",[ls]:"fire-app-check-compat",[ds]:"fire-auth",[hs]:"fire-auth-compat",[ps]:"fire-rtdb",[fs]:"fire-rtdb-compat",[ms]:"fire-fn",[bs]:"fire-fn-compat",[gs]:"fire-iid",[Es]:"fire-iid-compat",[ys]:"fire-fcm",[Ts]:"fire-fcm-compat",[_s]:"fire-perf",[Cs]:"fire-perf-compat",[Rs]:"fire-rc",[Ss]:"fire-rc-compat",[Is]:"fire-gcs",[qs]:"fire-gcs-compat",[ws]:"fire-fst",[As]:"fire-fst-compat","fire-js":"fire-js",[vs]:"fire-js-all"};/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ds=new Map,Ps=new Map,ot=new Map;function it(t,e){try{t.container.addComponent(e)}catch(r){z.debug(`Component ${e.name} failed to register with FirebaseApp ${t.name}`,r)}}function j(t){const e=t.name;if(ot.has(e))return z.debug(`There were multiple attempts to register component ${e}.`),!1;ot.set(e,t);for(const r of Ds.values())it(r,t);for(const r of Ps.values())it(r,t);return!0}function Nt(t,e){const r=t.container.getProvider("heartbeat").getImmediate({optional:!0});return r&&r.triggerHeartbeat(),t.container.getProvider(e)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ks={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},xe=new Ft("app","Firebase",ks);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Ns=Os;function D(t,e,r){var s;let n=(s=Fs[t])!==null&&s!==void 0?s:t;r&&(n+=`-${r}`);const o=n.match(/\s|\//),i=e.match(/\s|\//);if(o||i){const a=[`Unable to register library "${n}" with version "${e}":`];o&&a.push(`library name "${n}" contains illegal characters (whitespace or "/")`),o&&i&&a.push("and"),i&&a.push(`version name "${e}" contains illegal characters (whitespace or "/")`),z.warn(a.join(" "));return}j(new Oe(`${n}-version`,()=>({library:n,version:e}),"VERSION"))}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Us="firebase-heartbeat-database",Ls=1,ne="firebase-heartbeat-store";let Ce=null;function Ut(){return Ce||(Ce=kt(Us,Ls,{upgrade:(t,e)=>{switch(e){case 0:try{t.createObjectStore(ne)}catch(r){console.warn(r)}}}}).catch(t=>{throw xe.create("idb-open",{originalErrorMessage:t.message})})),Ce}async function Bs(t){try{const r=(await Ut()).transaction(ne),s=await r.objectStore(ne).get(Lt(t));return await r.done,s}catch(e){if(e instanceof He)z.warn(e.message);else{const r=xe.create("idb-get",{originalErrorMessage:e==null?void 0:e.message});z.warn(r.message)}}}async function at(t,e){try{const s=(await Ut()).transaction(ne,"readwrite");await s.objectStore(ne).put(e,Lt(t)),await s.done}catch(r){if(r instanceof He)z.warn(r.message);else{const s=xe.create("idb-set",{originalErrorMessage:r==null?void 0:r.message});z.warn(s.message)}}}function Lt(t){return`${t.name}!${t.options.appId}`}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const $s=1024,Ms=30*24*60*60*1e3;class Hs{constructor(e){this.container=e,this._heartbeatsCache=null;const r=this.container.getProvider("app").getImmediate();this._storage=new xs(r),this._heartbeatsCachePromise=this._storage.read().then(s=>(this._heartbeatsCache=s,s))}async triggerHeartbeat(){var e,r;const n=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),o=ct();if(!(((e=this._heartbeatsCache)===null||e===void 0?void 0:e.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((r=this._heartbeatsCache)===null||r===void 0?void 0:r.heartbeats)==null))&&!(this._heartbeatsCache.lastSentHeartbeatDate===o||this._heartbeatsCache.heartbeats.some(i=>i.date===o)))return this._heartbeatsCache.heartbeats.push({date:o,agent:n}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(i=>{const a=new Date(i.date).valueOf();return Date.now()-a<=Ms}),this._storage.overwrite(this._heartbeatsCache)}async getHeartbeatsHeader(){var e;if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((e=this._heartbeatsCache)===null||e===void 0?void 0:e.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const r=ct(),{heartbeatsToSend:s,unsentEntries:n}=js(this._heartbeatsCache.heartbeats),o=vt(JSON.stringify({version:2,heartbeats:s}));return this._heartbeatsCache.lastSentHeartbeatDate=r,n.length>0?(this._heartbeatsCache.heartbeats=n,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),o}}function ct(){return new Date().toISOString().substring(0,10)}function js(t,e=$s){const r=[];let s=t.slice();for(const n of t){const o=r.find(i=>i.agent===n.agent);if(o){if(o.dates.push(n.date),lt(r)>e){o.dates.pop();break}}else if(r.push({agent:n.agent,dates:[n.date]}),lt(r)>e){r.pop();break}s=s.slice(1)}return{heartbeatsToSend:r,unsentEntries:s}}class xs{constructor(e){this.app=e,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return Br()?$r().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const r=await Bs(this.app);return r!=null&&r.heartbeats?r:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(e){var r;if(await this._canUseIndexedDBPromise){const n=await this.read();return at(this.app,{lastSentHeartbeatDate:(r=e.lastSentHeartbeatDate)!==null&&r!==void 0?r:n.lastSentHeartbeatDate,heartbeats:e.heartbeats})}else return}async add(e){var r;if(await this._canUseIndexedDBPromise){const n=await this.read();return at(this.app,{lastSentHeartbeatDate:(r=e.lastSentHeartbeatDate)!==null&&r!==void 0?r:n.lastSentHeartbeatDate,heartbeats:[...n.heartbeats,...e.heartbeats]})}else return}}function lt(t){return vt(JSON.stringify({version:2,heartbeats:t})).length}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Gs(t){j(new Oe("platform-logger",e=>new ns(e),"PRIVATE")),j(new Oe("heartbeat",e=>new Hs(e),"PRIVATE")),D(Pe,nt,t),D(Pe,nt,"esm2017"),D("fire-js","")}Gs("");/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */var m;(function(t){t[t.DEBUG=0]="DEBUG",t[t.VERBOSE=1]="VERBOSE",t[t.INFO=2]="INFO",t[t.WARN=3]="WARN",t[t.ERROR=4]="ERROR",t[t.SILENT=5]="SILENT"})(m||(m={}));const Vs={debug:m.DEBUG,verbose:m.VERBOSE,info:m.INFO,warn:m.WARN,error:m.ERROR,silent:m.SILENT},Ks=m.INFO,Ws={[m.DEBUG]:"log",[m.VERBOSE]:"log",[m.INFO]:"info",[m.WARN]:"warn",[m.ERROR]:"error"},zs=(t,e,...r)=>{if(e<t.logLevel)return;const s=new Date().toISOString(),n=Ws[e];if(n)console[n](`[${s}]  ${t.name}:`,...r);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};class Bt{constructor(e){this.name=e,this._logLevel=Ks,this._logHandler=zs,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in m))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?Vs[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,m.DEBUG,...e),this._logHandler(this,m.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,m.VERBOSE,...e),this._logHandler(this,m.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,m.INFO,...e),this._logHandler(this,m.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,m.WARN,...e),this._logHandler(this,m.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,m.ERROR,...e),this._logHandler(this,m.ERROR,...e)}}function Js(){const t=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof t=="object"&&t.id!==void 0}function $t(){try{return typeof indexedDB=="object"}catch{return!1}}function Ys(){return new Promise((t,e)=>{try{let r=!0;const s="validate-browser-context-for-indexeddb-analytics-module",n=self.indexedDB.open(s);n.onsuccess=()=>{n.result.close(),r||self.indexedDB.deleteDatabase(s),t(!0)},n.onupgradeneeded=()=>{r=!1},n.onerror=()=>{var o;e(((o=n.error)===null||o===void 0?void 0:o.message)||"")}}catch(r){e(r)}})}function Qs(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
 * @license
 * Copyright 2017 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Xs="FirebaseError";class ee extends Error{constructor(e,r,s){super(r),this.code=e,this.customData=s,this.name=Xs,Object.setPrototypeOf(this,ee.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,me.prototype.create)}}class me{constructor(e,r,s){this.service=e,this.serviceName=r,this.errors=s}create(e,...r){const s=r[0]||{},n=`${this.service}/${e}`,o=this.errors[e],i=o?Zs(o,s):"Error",a=`${this.serviceName}: ${i} (${n}).`;return new ee(n,a,s)}}function Zs(t,e){return t.replace(en,(r,s)=>{const n=e[s];return n!=null?String(n):`<${s}?>`})}const en=/\{\$([^}]+)}/g;/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const tn=1e3,rn=2,sn=4*60*60*1e3,nn=.5;function ke(t,e=tn,r=rn){const s=e*Math.pow(r,t),n=Math.round(nn*s*(Math.random()-.5)*2);return Math.min(sn,s+n)}/**
 * @license
 * Copyright 2021 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Mt(t){return t&&t._delegate?t._delegate:t}class oe{constructor(e,r,s){this.name=e,this.instanceFactory=r,this.type=s,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}}const Ht="@firebase/installations",Ge="0.6.7";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const jt=1e4,xt=`w:${Ge}`,Gt="FIS_v2",on="https://firebaseinstallations.googleapis.com/v1",an=60*60*1e3,cn="installations",ln="Installations";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const un={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},J=new me(cn,ln,un);function Vt(t){return t instanceof ee&&t.code.includes("request-failed")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Kt({projectId:t}){return`${on}/projects/${t}/installations`}function Wt(t){return{token:t.token,requestStatus:2,expiresIn:hn(t.expiresIn),creationTime:Date.now()}}async function zt(t,e){const s=(await e.json()).error;return J.create("request-failed",{requestName:t,serverCode:s.code,serverMessage:s.message,serverStatus:s.status})}function Jt({apiKey:t}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":t})}function dn(t,{refreshToken:e}){const r=Jt(t);return r.append("Authorization",pn(e)),r}async function Yt(t){const e=await t();return e.status>=500&&e.status<600?t():e}function hn(t){return Number(t.replace("s","000"))}function pn(t){return`${Gt} ${t}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function fn({appConfig:t,heartbeatServiceProvider:e},{fid:r}){const s=Kt(t),n=Jt(t),o=e.getImmediate({optional:!0});if(o){const l=await o.getHeartbeatsHeader();l&&n.append("x-firebase-client",l)}const i={fid:r,authVersion:Gt,appId:t.appId,sdkVersion:xt},a={method:"POST",headers:n,body:JSON.stringify(i)},c=await Yt(()=>fetch(s,a));if(c.ok){const l=await c.json();return{fid:l.fid||r,registrationStatus:2,refreshToken:l.refreshToken,authToken:Wt(l.authToken)}}else throw await zt("Create Installation",c)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Qt(t){return new Promise(e=>{setTimeout(e,t)})}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function mn(t){return btoa(String.fromCharCode(...t)).replace(/\+/g,"-").replace(/\//g,"_")}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const bn=/^[cdef][\w-]{21}$/,Ne="";function gn(){try{const t=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(t),t[0]=112+t[0]%16;const r=En(t);return bn.test(r)?r:Ne}catch{return Ne}}function En(t){return mn(t).substr(0,22)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function be(t){return`${t.appName}!${t.appId}`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Xt=new Map;function Zt(t,e){const r=be(t);er(r,e),yn(r,e)}function er(t,e){const r=Xt.get(t);if(r)for(const s of r)s(e)}function yn(t,e){const r=Tn();r&&r.postMessage({key:t,fid:e}),_n()}let G=null;function Tn(){return!G&&"BroadcastChannel"in self&&(G=new BroadcastChannel("[Firebase] FID Change"),G.onmessage=t=>{er(t.data.key,t.data.fid)}),G}function _n(){Xt.size===0&&G&&(G.close(),G=null)}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Cn="firebase-installations-database",Rn=1,Y="firebase-installations-store";let Re=null;function Ve(){return Re||(Re=kt(Cn,Rn,{upgrade:(t,e)=>{switch(e){case 0:t.createObjectStore(Y)}}})),Re}async function fe(t,e){const r=be(t),n=(await Ve()).transaction(Y,"readwrite"),o=n.objectStore(Y),i=await o.get(r);return await o.put(e,r),await n.done,(!i||i.fid!==e.fid)&&Zt(t,e.fid),e}async function tr(t){const e=be(t),s=(await Ve()).transaction(Y,"readwrite");await s.objectStore(Y).delete(e),await s.done}async function ge(t,e){const r=be(t),n=(await Ve()).transaction(Y,"readwrite"),o=n.objectStore(Y),i=await o.get(r),a=e(i);return a===void 0?await o.delete(r):await o.put(a,r),await n.done,a&&(!i||i.fid!==a.fid)&&Zt(t,a.fid),a}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Ke(t){let e;const r=await ge(t.appConfig,s=>{const n=Sn(s),o=In(t,n);return e=o.registrationPromise,o.installationEntry});return r.fid===Ne?{installationEntry:await e}:{installationEntry:r,registrationPromise:e}}function Sn(t){const e=t||{fid:gn(),registrationStatus:0};return rr(e)}function In(t,e){if(e.registrationStatus===0){if(!navigator.onLine){const n=Promise.reject(J.create("app-offline"));return{installationEntry:e,registrationPromise:n}}const r={fid:e.fid,registrationStatus:1,registrationTime:Date.now()},s=qn(t,r);return{installationEntry:r,registrationPromise:s}}else return e.registrationStatus===1?{installationEntry:e,registrationPromise:wn(t)}:{installationEntry:e}}async function qn(t,e){try{const r=await fn(t,e);return fe(t.appConfig,r)}catch(r){throw Vt(r)&&r.customData.serverCode===409?await tr(t.appConfig):await fe(t.appConfig,{fid:e.fid,registrationStatus:0}),r}}async function wn(t){let e=await ut(t.appConfig);for(;e.registrationStatus===1;)await Qt(100),e=await ut(t.appConfig);if(e.registrationStatus===0){const{installationEntry:r,registrationPromise:s}=await Ke(t);return s||r}return e}function ut(t){return ge(t,e=>{if(!e)throw J.create("installation-not-found");return rr(e)})}function rr(t){return An(t)?{fid:t.fid,registrationStatus:0}:t}function An(t){return t.registrationStatus===1&&t.registrationTime+jt<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function vn({appConfig:t,heartbeatServiceProvider:e},r){const s=On(t,r),n=dn(t,r),o=e.getImmediate({optional:!0});if(o){const l=await o.getHeartbeatsHeader();l&&n.append("x-firebase-client",l)}const i={installation:{sdkVersion:xt,appId:t.appId}},a={method:"POST",headers:n,body:JSON.stringify(i)},c=await Yt(()=>fetch(s,a));if(c.ok){const l=await c.json();return Wt(l)}else throw await zt("Generate Auth Token",c)}function On(t,{fid:e}){return`${Kt(t)}/${e}/authTokens:generate`}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function We(t,e=!1){let r;const s=await ge(t.appConfig,o=>{if(!sr(o))throw J.create("not-registered");const i=o.authToken;if(!e&&Pn(i))return o;if(i.requestStatus===1)return r=Fn(t,e),o;{if(!navigator.onLine)throw J.create("app-offline");const a=Nn(o);return r=Dn(t,a),a}});return r?await r:s.authToken}async function Fn(t,e){let r=await dt(t.appConfig);for(;r.authToken.requestStatus===1;)await Qt(100),r=await dt(t.appConfig);const s=r.authToken;return s.requestStatus===0?We(t,e):s}function dt(t){return ge(t,e=>{if(!sr(e))throw J.create("not-registered");const r=e.authToken;return Un(r)?Object.assign(Object.assign({},e),{authToken:{requestStatus:0}}):e})}async function Dn(t,e){try{const r=await vn(t,e),s=Object.assign(Object.assign({},e),{authToken:r});return await fe(t.appConfig,s),r}catch(r){if(Vt(r)&&(r.customData.serverCode===401||r.customData.serverCode===404))await tr(t.appConfig);else{const s=Object.assign(Object.assign({},e),{authToken:{requestStatus:0}});await fe(t.appConfig,s)}throw r}}function sr(t){return t!==void 0&&t.registrationStatus===2}function Pn(t){return t.requestStatus===2&&!kn(t)}function kn(t){const e=Date.now();return e<t.creationTime||t.creationTime+t.expiresIn<e+an}function Nn(t){const e={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},t),{authToken:e})}function Un(t){return t.requestStatus===1&&t.requestTime+jt<Date.now()}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Ln(t){const e=t,{installationEntry:r,registrationPromise:s}=await Ke(e);return s?s.catch(console.error):We(e).catch(console.error),r.fid}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function Bn(t,e=!1){const r=t;return await $n(r),(await We(r,e)).token}async function $n(t){const{registrationPromise:e}=await Ke(t);e&&await e}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Mn(t){if(!t||!t.options)throw Se("App Configuration");if(!t.name)throw Se("App Name");const e=["projectId","apiKey","appId"];for(const r of e)if(!t.options[r])throw Se(r);return{appName:t.name,projectId:t.options.projectId,apiKey:t.options.apiKey,appId:t.options.appId}}function Se(t){return J.create("missing-app-config-values",{valueName:t})}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const nr="installations",Hn="installations-internal",jn=t=>{const e=t.getProvider("app").getImmediate(),r=Mn(e),s=Nt(e,"heartbeat");return{app:e,appConfig:r,heartbeatServiceProvider:s,_delete:()=>Promise.resolve()}},xn=t=>{const e=t.getProvider("app").getImmediate(),r=Nt(e,nr).getImmediate();return{getId:()=>Ln(r),getToken:n=>Bn(r,n)}};function Gn(){j(new oe(nr,jn,"PUBLIC")),j(new oe(Hn,xn,"PRIVATE"))}Gn();D(Ht,Ge);D(Ht,Ge,"esm2017");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const ht="analytics",Vn="firebase_id",Kn="origin",Wn=60*1e3,zn="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",ze="https://www.googletagmanager.com/gtag/js";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const T=new Bt("@firebase/analytics");/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Jn={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-intialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},_=new me("analytics","Analytics",Jn);/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Yn(t){if(!t.startsWith(ze)){const e=_.create("invalid-gtag-resource",{gtagURL:t});return T.warn(e.message),""}return t}function or(t){return Promise.all(t.map(e=>e.catch(r=>r)))}function Qn(t,e){let r;return window.trustedTypes&&(r=window.trustedTypes.createPolicy(t,e)),r}function Xn(t,e){const r=Qn("firebase-js-sdk-policy",{createScriptURL:Yn}),s=document.createElement("script"),n=`${ze}?l=${t}&id=${e}`;s.src=r?r==null?void 0:r.createScriptURL(n):n,s.async=!0,document.head.appendChild(s)}function Zn(t){let e=[];return Array.isArray(window[t])?e=window[t]:window[t]=e,e}async function eo(t,e,r,s,n,o){const i=s[n];try{if(i)await e[i];else{const c=(await or(r)).find(l=>l.measurementId===n);c&&await e[c.appId]}}catch(a){T.error(a)}t("config",n,o)}async function to(t,e,r,s,n){try{let o=[];if(n&&n.send_to){let i=n.send_to;Array.isArray(i)||(i=[i]);const a=await or(r);for(const c of i){const l=a.find(p=>p.measurementId===c),d=l&&e[l.appId];if(d)o.push(d);else{o=[];break}}}o.length===0&&(o=Object.values(e)),await Promise.all(o),t("event",s,n||{})}catch(o){T.error(o)}}function ro(t,e,r,s){async function n(o,...i){try{if(o==="event"){const[a,c]=i;await to(t,e,r,a,c)}else if(o==="config"){const[a,c]=i;await eo(t,e,r,s,a,c)}else if(o==="consent"){const[a]=i;t("consent","update",a)}else if(o==="get"){const[a,c,l]=i;t("get",a,c,l)}else if(o==="set"){const[a]=i;t("set",a)}else t(o,...i)}catch(a){T.error(a)}}return n}function so(t,e,r,s,n){let o=function(...i){window[s].push(arguments)};return window[n]&&typeof window[n]=="function"&&(o=window[n]),window[n]=ro(o,t,e,r),{gtagCore:o,wrappedGtag:window[n]}}function no(t){const e=window.document.getElementsByTagName("script");for(const r of Object.values(e))if(r.src&&r.src.includes(ze)&&r.src.includes(t))return r;return null}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const oo=30,io=1e3;class ao{constructor(e={},r=io){this.throttleMetadata=e,this.intervalMillis=r}getThrottleMetadata(e){return this.throttleMetadata[e]}setThrottleMetadata(e,r){this.throttleMetadata[e]=r}deleteThrottleMetadata(e){delete this.throttleMetadata[e]}}const ir=new ao;function co(t){return new Headers({Accept:"application/json","x-goog-api-key":t})}async function lo(t){var e;const{appId:r,apiKey:s}=t,n={method:"GET",headers:co(s)},o=zn.replace("{app-id}",r),i=await fetch(o,n);if(i.status!==200&&i.status!==304){let a="";try{const c=await i.json();!((e=c.error)===null||e===void 0)&&e.message&&(a=c.error.message)}catch{}throw _.create("config-fetch-failed",{httpStatus:i.status,responseMessage:a})}return i.json()}async function uo(t,e=ir,r){const{appId:s,apiKey:n,measurementId:o}=t.options;if(!s)throw _.create("no-app-id");if(!n){if(o)return{measurementId:o,appId:s};throw _.create("no-api-key")}const i=e.getThrottleMetadata(s)||{backoffCount:0,throttleEndTimeMillis:Date.now()},a=new fo;return setTimeout(async()=>{a.abort()},r!==void 0?r:Wn),ar({appId:s,apiKey:n,measurementId:o},i,a,e)}async function ar(t,{throttleEndTimeMillis:e,backoffCount:r},s,n=ir){var o;const{appId:i,measurementId:a}=t;try{await ho(s,e)}catch(c){if(a)return T.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${a} provided in the "measurementId" field in the local Firebase config. [${c==null?void 0:c.message}]`),{appId:i,measurementId:a};throw c}try{const c=await lo(t);return n.deleteThrottleMetadata(i),c}catch(c){const l=c;if(!po(l)){if(n.deleteThrottleMetadata(i),a)return T.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${a} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:a};throw c}const d=Number((o=l==null?void 0:l.customData)===null||o===void 0?void 0:o.httpStatus)===503?ke(r,n.intervalMillis,oo):ke(r,n.intervalMillis),p={throttleEndTimeMillis:Date.now()+d,backoffCount:r+1};return n.setThrottleMetadata(i,p),T.debug(`Calling attemptFetch again in ${d} millis`),ar(t,p,s,n)}}function ho(t,e){return new Promise((r,s)=>{const n=Math.max(e-Date.now(),0),o=setTimeout(r,n);t.addEventListener(()=>{clearTimeout(o),s(_.create("fetch-throttle",{throttleEndTimeMillis:e}))})})}function po(t){if(!(t instanceof ee)||!t.customData)return!1;const e=Number(t.customData.httpStatus);return e===429||e===500||e===503||e===504}class fo{constructor(){this.listeners=[]}addEventListener(e){this.listeners.push(e)}abort(){this.listeners.forEach(e=>e())}}async function mo(t,e,r,s,n){if(n&&n.global){t("event",r,s);return}else{const o=await e,i=Object.assign(Object.assign({},s),{send_to:o});t("event",r,i)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */async function bo(){if($t())try{await Ys()}catch(t){return T.warn(_.create("indexeddb-unavailable",{errorInfo:t==null?void 0:t.toString()}).message),!1}else return T.warn(_.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function go(t,e,r,s,n,o,i){var a;const c=uo(t);c.then(E=>{r[E.measurementId]=E.appId,t.options.measurementId&&E.measurementId!==t.options.measurementId&&T.warn(`The measurement ID in the local Firebase config (${t.options.measurementId}) does not match the measurement ID fetched from the server (${E.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(E=>T.error(E)),e.push(c);const l=bo().then(E=>{if(E)return s.getId()}),[d,p]=await Promise.all([c,l]);no(o)||Xn(o,d.measurementId),n("js",new Date);const f=(a=i==null?void 0:i.config)!==null&&a!==void 0?a:{};return f[Kn]="firebase",f.update=!0,p!=null&&(f[Vn]=p),n("config",d.measurementId,f),d.measurementId}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Eo{constructor(e){this.app=e}_delete(){return delete se[this.app.options.appId],Promise.resolve()}}let se={},pt=[];const ft={};let Ie="dataLayer",yo="gtag",mt,cr,bt=!1;function To(){const t=[];if(Js()&&t.push("This is a browser extension environment."),Qs()||t.push("Cookies are not available."),t.length>0){const e=t.map((s,n)=>`(${n+1}) ${s}`).join(" "),r=_.create("invalid-analytics-context",{errorInfo:e});T.warn(r.message)}}function _o(t,e,r){To();const s=t.options.appId;if(!s)throw _.create("no-app-id");if(!t.options.apiKey)if(t.options.measurementId)T.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${t.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw _.create("no-api-key");if(se[s]!=null)throw _.create("already-exists",{id:s});if(!bt){Zn(Ie);const{wrappedGtag:o,gtagCore:i}=so(se,pt,ft,Ie,yo);cr=o,mt=i,bt=!0}return se[s]=go(t,pt,ft,e,mt,Ie,r),new Eo(t)}function Co(t,e,r,s){t=Mt(t),mo(cr,se[t.app.options.appId],e,r,s).catch(n=>T.error(n))}const gt="@firebase/analytics",Et="0.10.3";function Ro(){j(new oe(ht,(e,{options:r})=>{const s=e.getProvider("app").getImmediate(),n=e.getProvider("installations-internal").getImmediate();return _o(s,n,r)},"PUBLIC")),j(new oe("analytics-internal",t,"PRIVATE")),D(gt,Et),D(gt,Et,"esm2017");function t(e){try{const r=e.getProvider(ht).getImmediate();return{logEvent:(s,n,o)=>Co(r,s,n,o)}}catch(r){throw _.create("interop-component-reg-failed",{reason:r})}}}Ro();const qe="@firebase/remote-config",yt="0.4.7";/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const So="remote-config";/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Io={"registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser"},y=new me("remoteconfig","Remote Config",Io);function qo(t){const e=Mt(t);return e._initializePromise||(e._initializePromise=e._storageCache.loadFromStorage().then(()=>{e._isInitializationComplete=!0})),e._initializePromise}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class wo{constructor(e,r,s,n){this.client=e,this.storage=r,this.storageCache=s,this.logger=n}isCachedDataFresh(e,r){if(!r)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const s=Date.now()-r,n=s<=e;return this.logger.debug(`Config fetch cache check. Cache age millis: ${s}. Cache max age millis (minimumFetchIntervalMillis setting): ${e}. Is cache hit: ${n}.`),n}async fetch(e){const[r,s]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(s&&this.isCachedDataFresh(e.cacheMaxAgeMillis,r))return s;e.eTag=s&&s.eTag;const n=await this.client.fetch(e),o=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return n.status===200&&o.push(this.storage.setLastSuccessfulFetchResponse(n)),await Promise.all(o),n}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ao(t=navigator){return t.languages&&t.languages[0]||t.language}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class vo{constructor(e,r,s,n,o,i){this.firebaseInstallations=e,this.sdkVersion=r,this.namespace=s,this.projectId=n,this.apiKey=o,this.appId=i}async fetch(e){const[r,s]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),o=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":e.eTag||"*"},a={sdk_version:this.sdkVersion,app_instance_id:r,app_instance_id_token:s,app_id:this.appId,language_code:Ao()},c={method:"POST",headers:i,body:JSON.stringify(a)},l=fetch(o,c),d=new Promise((C,k)=>{e.signal.addEventListener(()=>{const Ze=new Error("The operation was aborted.");Ze.name="AbortError",k(Ze)})});let p;try{await Promise.race([l,d]),p=await l}catch(C){let k="fetch-client-network";throw(C==null?void 0:C.name)==="AbortError"&&(k="fetch-timeout"),y.create(k,{originalErrorMessage:C==null?void 0:C.message})}let f=p.status;const E=p.headers.get("ETag")||void 0;let P,te;if(p.status===200){let C;try{C=await p.json()}catch(k){throw y.create("fetch-client-parse",{originalErrorMessage:k==null?void 0:k.message})}P=C.entries,te=C.state}if(te==="INSTANCE_STATE_UNSPECIFIED"?f=500:te==="NO_CHANGE"?f=304:(te==="NO_TEMPLATE"||te==="EMPTY_CONFIG")&&(P={}),f!==304&&f!==200)throw y.create("fetch-status",{httpStatus:f});return{status:f,eTag:E,config:P}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Oo(t,e){return new Promise((r,s)=>{const n=Math.max(e-Date.now(),0),o=setTimeout(r,n);t.addEventListener(()=>{clearTimeout(o),s(y.create("fetch-throttle",{throttleEndTimeMillis:e}))})})}function Fo(t){if(!(t instanceof ee)||!t.customData)return!1;const e=Number(t.customData.httpStatus);return e===429||e===500||e===503||e===504}class Do{constructor(e,r){this.client=e,this.storage=r}async fetch(e){const r=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(e,r)}async attemptFetch(e,{throttleEndTimeMillis:r,backoffCount:s}){await Oo(e.signal,r);try{const n=await this.client.fetch(e);return await this.storage.deleteThrottleMetadata(),n}catch(n){if(!Fo(n))throw n;const o={throttleEndTimeMillis:Date.now()+ke(s),backoffCount:s+1};return await this.storage.setThrottleMetadata(o),this.attemptFetch(e,o)}}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */const Po=60*1e3,ko=12*60*60*1e3;class No{constructor(e,r,s,n,o){this.app=e,this._client=r,this._storageCache=s,this._storage=n,this._logger=o,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:Po,minimumFetchIntervalMillis:ko},this.defaultConfig={}}get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function pe(t,e){const r=t.target.error||void 0;return y.create(e,{originalErrorMessage:r&&(r==null?void 0:r.message)})}const x="app_namespace_store",Uo="firebase_remote_config",Lo=1;function Bo(){return new Promise((t,e)=>{try{const r=indexedDB.open(Uo,Lo);r.onerror=s=>{e(pe(s,"storage-open"))},r.onsuccess=s=>{t(s.target.result)},r.onupgradeneeded=s=>{const n=s.target.result;switch(s.oldVersion){case 0:n.createObjectStore(x,{keyPath:"compositeKey"})}}}catch(r){e(y.create("storage-open",{originalErrorMessage:r==null?void 0:r.message}))}})}class $o{constructor(e,r,s,n=Bo()){this.appId=e,this.appName=r,this.namespace=s,this.openDbPromise=n}getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(e){return this.set("last_fetch_status",e)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(e){return this.set("last_successful_fetch_timestamp_millis",e)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(e){return this.set("last_successful_fetch_response",e)}getActiveConfig(){return this.get("active_config")}setActiveConfig(e){return this.set("active_config",e)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(e){return this.set("active_config_etag",e)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(e){return this.set("throttle_metadata",e)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}async get(e){const r=await this.openDbPromise;return new Promise((s,n)=>{const i=r.transaction([x],"readonly").objectStore(x),a=this.createCompositeKey(e);try{const c=i.get(a);c.onerror=l=>{n(pe(l,"storage-get"))},c.onsuccess=l=>{const d=l.target.result;s(d?d.value:void 0)}}catch(c){n(y.create("storage-get",{originalErrorMessage:c==null?void 0:c.message}))}})}async set(e,r){const s=await this.openDbPromise;return new Promise((n,o)=>{const a=s.transaction([x],"readwrite").objectStore(x),c=this.createCompositeKey(e);try{const l=a.put({compositeKey:c,value:r});l.onerror=d=>{o(pe(d,"storage-set"))},l.onsuccess=()=>{n()}}catch(l){o(y.create("storage-set",{originalErrorMessage:l==null?void 0:l.message}))}})}async delete(e){const r=await this.openDbPromise;return new Promise((s,n)=>{const i=r.transaction([x],"readwrite").objectStore(x),a=this.createCompositeKey(e);try{const c=i.delete(a);c.onerror=l=>{n(pe(l,"storage-delete"))},c.onsuccess=()=>{s()}}catch(c){n(y.create("storage-delete",{originalErrorMessage:c==null?void 0:c.message}))}})}createCompositeKey(e){return[this.appId,this.appName,this.namespace,e].join()}}/**
 * @license
 * Copyright 2019 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */class Mo{constructor(e){this.storage=e}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}async loadFromStorage(){const e=this.storage.getLastFetchStatus(),r=this.storage.getLastSuccessfulFetchTimestampMillis(),s=this.storage.getActiveConfig(),n=await e;n&&(this.lastFetchStatus=n);const o=await r;o&&(this.lastSuccessfulFetchTimestampMillis=o);const i=await s;i&&(this.activeConfig=i)}setLastFetchStatus(e){return this.lastFetchStatus=e,this.storage.setLastFetchStatus(e)}setLastSuccessfulFetchTimestampMillis(e){return this.lastSuccessfulFetchTimestampMillis=e,this.storage.setLastSuccessfulFetchTimestampMillis(e)}setActiveConfig(e){return this.activeConfig=e,this.storage.setActiveConfig(e)}}/**
 * @license
 * Copyright 2020 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */function Ho(){j(new oe(So,t,"PUBLIC").setMultipleInstances(!0)),D(qe,yt),D(qe,yt,"esm2017");function t(e,{instanceIdentifier:r}){const s=e.getProvider("app").getImmediate(),n=e.getProvider("installations-internal").getImmediate();if(typeof window>"u")throw y.create("registration-window");if(!$t())throw y.create("indexed-db-unavailable");const{projectId:o,apiKey:i,appId:a}=s.options;if(!o)throw y.create("registration-project-id");if(!i)throw y.create("registration-api-key");if(!a)throw y.create("registration-app-id");r=r||"firebase";const c=new $o(a,s.name,r),l=new Mo(c),d=new Bt(qe);d.logLevel=m.ERROR;const p=new vo(n,Ns,r,o,i,a),f=new Do(p,c),E=new wo(f,c,l,d),P=new No(s,E,l,c,d);return qo(P),P}}Ho();let jo=class{constructor(e){this.config=e}},Ue=class extends Error{constructor(e,r,s){super(s),this.name="ApiError",this.url=r.url,this.status=r.status,this.statusText=r.statusText,this.body=r.body,this.request=e}},xo=class extends Error{constructor(e){super(e),this.name="CancelError"}get isCancelled(){return!0}};var A,v,S,L,K,X,B,Ct;let Go=(Ct=class{constructor(e){g(this,A,void 0);g(this,v,void 0);g(this,S,void 0);g(this,L,void 0);g(this,K,void 0);g(this,X,void 0);g(this,B,void 0);h(this,A,!1),h(this,v,!1),h(this,S,!1),h(this,L,[]),h(this,K,new Promise((r,s)=>{h(this,X,r),h(this,B,s);const n=a=>{u(this,A)||u(this,v)||u(this,S)||(h(this,A,!0),u(this,X)&&u(this,X).call(this,a))},o=a=>{u(this,A)||u(this,v)||u(this,S)||(h(this,v,!0),u(this,B)&&u(this,B).call(this,a))},i=a=>{u(this,A)||u(this,v)||u(this,S)||u(this,L).push(a)};return Object.defineProperty(i,"isResolved",{get:()=>u(this,A)}),Object.defineProperty(i,"isRejected",{get:()=>u(this,v)}),Object.defineProperty(i,"isCancelled",{get:()=>u(this,S)}),e(n,o,i)}))}get[Symbol.toStringTag](){return"Cancellable Promise"}then(e,r){return u(this,K).then(e,r)}catch(e){return u(this,K).catch(e)}finally(e){return u(this,K).finally(e)}cancel(){if(!(u(this,A)||u(this,v)||u(this,S))){if(h(this,S,!0),u(this,L).length)try{for(const e of u(this,L))e()}catch(e){console.warn("Cancellation threw an error",e);return}u(this,L).length=0,u(this,B)&&u(this,B).call(this,new xo("Request aborted"))}}get isCancelled(){return u(this,S)}},A=new WeakMap,v=new WeakMap,S=new WeakMap,L=new WeakMap,K=new WeakMap,X=new WeakMap,B=new WeakMap,Ct);const Je=t=>t!=null,ae=t=>typeof t=="string",we=t=>ae(t)&&t!=="",Ye=t=>typeof t=="object"&&typeof t.type=="string"&&typeof t.stream=="function"&&typeof t.arrayBuffer=="function"&&typeof t.constructor=="function"&&typeof t.constructor.name=="string"&&/^(Blob|File)$/.test(t.constructor.name)&&/^(Blob|File)$/.test(t[Symbol.toStringTag]),lr=t=>t instanceof FormData,Vo=t=>{try{return btoa(t)}catch{return Buffer.from(t).toString("base64")}},Ko=t=>{const e=[],r=(n,o)=>{e.push(`${encodeURIComponent(n)}=${encodeURIComponent(String(o))}`)},s=(n,o)=>{Je(o)&&(Array.isArray(o)?o.forEach(i=>{s(n,i)}):typeof o=="object"?Object.entries(o).forEach(([i,a])=>{s(`${n}[${i}]`,a)}):r(n,o))};return Object.entries(t).forEach(([n,o])=>{s(n,o)}),e.length>0?`?${e.join("&")}`:""},Wo=(t,e)=>{const r=t.ENCODE_PATH||encodeURI,s=e.url.replace("{api-version}",t.VERSION).replace(/{(.*?)}/g,(o,i)=>{var a;return(a=e.path)!=null&&a.hasOwnProperty(i)?r(String(e.path[i])):o}),n=`${t.BASE}${s}`;return e.query?`${n}${Ko(e.query)}`:n},zo=t=>{if(t.formData){const e=new FormData,r=(s,n)=>{ae(n)||Ye(n)?e.append(s,n):e.append(s,JSON.stringify(n))};return Object.entries(t.formData).filter(([s,n])=>Je(n)).forEach(([s,n])=>{Array.isArray(n)?n.forEach(o=>r(s,o)):r(s,n)}),e}},ue=async(t,e)=>typeof e=="function"?e(t):e,Jo=async(t,e)=>{const r=await ue(e,t.TOKEN),s=await ue(e,t.USERNAME),n=await ue(e,t.PASSWORD),o=await ue(e,t.HEADERS),i=Object.entries({Accept:"application/json",...o,...e.headers}).filter(([a,c])=>Je(c)).reduce((a,[c,l])=>({...a,[c]:String(l)}),{});if(we(r)&&(i.Authorization=`Bearer ${r}`),we(s)&&we(n)){const a=Vo(`${s}:${n}`);i.Authorization=`Basic ${a}`}return e.body&&(e.mediaType?i["Content-Type"]=e.mediaType:Ye(e.body)?i["Content-Type"]=e.body.type||"application/octet-stream":ae(e.body)?i["Content-Type"]="text/plain":lr(e.body)||(i["Content-Type"]="application/json")),new Headers(i)},Yo=t=>{var e;if(t.body)return(e=t.mediaType)!=null&&e.includes("/json")?JSON.stringify(t.body):ae(t.body)||Ye(t.body)||lr(t.body)?t.body:JSON.stringify(t.body)},Qo=(t,e,r,s,n,o,i)=>{const a=new AbortController,c={headers:o,body:s??n,method:e.method,signal:a.signal};return t.WITH_CREDENTIALS&&(c.credentials=t.CREDENTIALS),i(()=>a.abort()),fetch(r,c)},Xo=(t,e)=>{if(e){const r=t.headers.get(e);if(ae(r))return r}},Zo=async t=>{if(t.status!==204)try{const e=t.headers.get("Content-Type");if(e){const r=e.toLowerCase(),s=r.startsWith("application/json"),n=["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","application/vnd.ms-excel","text/csv"].some(o=>r.includes(o));return s?await t.json():n?await t.blob():await t.text()}}catch(e){console.error(e)}},ei=(t,e)=>{const s={400:"Bad Request",401:"Unauthorized",403:"Forbidden",404:"Not Found",500:"Internal Server Error",502:"Bad Gateway",503:"Service Unavailable",...t.errors}[e.status];if(e.status===503){window.location.assign(Be);return}if(s)throw new Ue(t,e,s);if(!e.ok)throw new Ue(t,e,"Generic Error")},ti=(t,e)=>new Go(async(r,s,n)=>{try{const o=Wo(t,e),i=zo(e),a=Yo(e),c=await Jo(t,e);if(!n.isCancelled){const l=await Qo(t,e,o,a,i,c,n),d=await Zo(l),p=Xo(l,e.responseHeader),f={url:o,ok:l.ok,status:l.status,statusText:l.statusText,body:p??d};ei(e,f),r(f.body)}}catch(o){if(o instanceof Ue&&o.status===401){if(o.url.includes("/adage-iframe")){window.location.href="/adage-iframe/erreur";return}if(!o.url.includes("/users/current")&&!o.url.includes("/users/signin")){window.location.href="/connexion";return}}s(o)}});let ri=class extends jo{constructor(e){super(e)}request(e){return ti(this.config,e)}};class si{constructor(e){this.httpRequest=e}authenticate(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/authenticate",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getAcademies(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/collective/academies",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}bookCollectiveOffer(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/collective/bookings",body:e,mediaType:"application/json",errors:{400:"Bad Request",403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveFavorites(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/collective/favorites",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getEducationalInstitutionWithBudget(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/collective/institution",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}deleteFavoriteForCollectiveOffer(e){return this.httpRequest.request({method:"DELETE",url:"/adage-iframe/collective/offer/{offer_id}/favorites",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveOfferTemplates(e){return this.httpRequest.request({method:"GET",url:"/adage-iframe/collective/offers-template/",query:{ids:e},errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}getCollectiveOfferTemplate(e){return this.httpRequest.request({method:"GET",url:"/adage-iframe/collective/offers-template/{offer_id}",path:{offer_id:e},errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}createCollectiveRequest(e,r){return this.httpRequest.request({method:"POST",url:"/adage-iframe/collective/offers-template/{offer_id}/request",path:{offer_id:e},body:r,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}getCollectiveOffersForMyInstitution(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/collective/offers/my_institution",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getCollectiveOffer(e){return this.httpRequest.request({method:"GET",url:"/adage-iframe/collective/offers/{offer_id}",path:{offer_id:e},errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}postCollectiveOfferFavorites(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/collective/offers/{offer_id}/favorites",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}deleteFavoriteForCollectiveOfferTemplate(e){return this.httpRequest.request({method:"DELETE",url:"/adage-iframe/collective/template/{offer_template_id}/favorites",path:{offer_template_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}postCollectiveTemplateFavorites(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/collective/templates/{offer_id}/favorites",path:{offer_id:e},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}listFeatures(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/features",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logBookingModalButtonClick(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/booking-modal-button",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logCatalogView(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/catalog-view",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logConsultPlaylistElement(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/consult-playlist-element",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logContactModalButtonClick(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/contact-modal-button",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logContactUrlClick(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/contact-url-click",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logFavOfferButtonClick(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/fav-offer/",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logHasSeenWholePlaylist(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/has-seen-whole-playlist/",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logHeaderLinkClick(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/header-link-click/",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logOfferDetailsButtonClick(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/offer-detail",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logOfferListViewSwitch(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/offer-list-view-switch",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logOfferTemplateDetailsButtonClick(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/offer-template-detail",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logHasSeenAllPlaylist(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/playlist",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logRequestFormPopinDismiss(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/request-popin-dismiss",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logOpenSatisfactionSurvey(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/sat-survey",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logSearchButtonClick(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/search-button",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logSearchShowMore(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/search-show-more",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logTrackingAutocompleteSuggestionClick(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/tracking-autocompletion",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logTrackingCtaShare(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/tracking-cta-share",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logTrackingFilter(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/tracking-filter",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}logTrackingMap(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/logs/tracking-map",body:e,mediaType:"application/json",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}getEducationalOffersCategories(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/offers/categories",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getEducationalOffersFormats(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/offers/formats",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getAnyNewTemplateOffersPlaylist(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/playlists/any_new_template_offers",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}getClassroomPlaylist(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/playlists/classroom",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getLocalOfferersPlaylist(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/playlists/local-offerers",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getNewOfferersPlaylist(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/playlists/new_offerers",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}newTemplateOffersPlaylist(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/playlists/new_template_offers",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}saveRedactorPreferences(e){return this.httpRequest.request({method:"POST",url:"/adage-iframe/redactor/preferences",body:e,mediaType:"application/json",errors:{403:"Forbidden",422:"Unprocessable Entity"}})}createAdageJwtFakeToken(){return this.httpRequest.request({method:"GET",url:"/adage-iframe/testing/token",errors:{403:"Forbidden",404:"Not Found",422:"Unprocessable Entity"}})}getVenueBySiret(e,r=!1){return this.httpRequest.request({method:"GET",url:"/adage-iframe/venues/siret/{siret}",path:{siret:e},query:{getRelative:r},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}getVenueById(e,r=!1){return this.httpRequest.request({method:"GET",url:"/adage-iframe/venues/{venue_id}",path:{venue_id:e},query:{getRelative:r},errors:{403:"Forbidden",422:"Unprocessable Entity"}})}}class ni{constructor(e,r=ri){this.request=new r({BASE:(e==null?void 0:e.BASE)??"http://localhost:5001",VERSION:(e==null?void 0:e.VERSION)??"0.1.0",WITH_CREDENTIALS:(e==null?void 0:e.WITH_CREDENTIALS)??!1,CREDENTIALS:(e==null?void 0:e.CREDENTIALS)??"include",TOKEN:e==null?void 0:e.TOKEN,USERNAME:e==null?void 0:e.USERNAME,PASSWORD:e==null?void 0:e.PASSWORD,HEADERS:e==null?void 0:e.HEADERS,ENCODE_PATH:e==null?void 0:e.ENCODE_PATH}),this.default=new si(this.request)}}class oi{constructor(e){this.config=e}}class Le extends Error{constructor(e,r,s){super(s),this.name="ApiError",this.url=r.url,this.status=r.status,this.statusText=r.statusText,this.body=r.body,this.request=e}}class ii extends Error{constructor(e){super(e),this.name="CancelError"}get isCancelled(){return!0}}var O,F,I,$,W,Z,M;class ai{constructor(e){g(this,O,void 0);g(this,F,void 0);g(this,I,void 0);g(this,$,void 0);g(this,W,void 0);g(this,Z,void 0);g(this,M,void 0);h(this,O,!1),h(this,F,!1),h(this,I,!1),h(this,$,[]),h(this,W,new Promise((r,s)=>{h(this,Z,r),h(this,M,s);const n=a=>{u(this,O)||u(this,F)||u(this,I)||(h(this,O,!0),u(this,Z)&&u(this,Z).call(this,a))},o=a=>{u(this,O)||u(this,F)||u(this,I)||(h(this,F,!0),u(this,M)&&u(this,M).call(this,a))},i=a=>{u(this,O)||u(this,F)||u(this,I)||u(this,$).push(a)};return Object.defineProperty(i,"isResolved",{get:()=>u(this,O)}),Object.defineProperty(i,"isRejected",{get:()=>u(this,F)}),Object.defineProperty(i,"isCancelled",{get:()=>u(this,I)}),e(n,o,i)}))}get[Symbol.toStringTag](){return"Cancellable Promise"}then(e,r){return u(this,W).then(e,r)}catch(e){return u(this,W).catch(e)}finally(e){return u(this,W).finally(e)}cancel(){if(!(u(this,O)||u(this,F)||u(this,I))){if(h(this,I,!0),u(this,$).length)try{for(const e of u(this,$))e()}catch(e){console.warn("Cancellation threw an error",e);return}u(this,$).length=0,u(this,M)&&u(this,M).call(this,new ii("Request aborted"))}}get isCancelled(){return u(this,I)}}O=new WeakMap,F=new WeakMap,I=new WeakMap,$=new WeakMap,W=new WeakMap,Z=new WeakMap,M=new WeakMap;const Qe=t=>t!=null,ce=t=>typeof t=="string",Ae=t=>ce(t)&&t!=="",Xe=t=>typeof t=="object"&&typeof t.type=="string"&&typeof t.stream=="function"&&typeof t.arrayBuffer=="function"&&typeof t.constructor=="function"&&typeof t.constructor.name=="string"&&/^(Blob|File)$/.test(t.constructor.name)&&/^(Blob|File)$/.test(t[Symbol.toStringTag]),ur=t=>t instanceof FormData,ci=t=>{try{return btoa(t)}catch{return Buffer.from(t).toString("base64")}},li=t=>{const e=[],r=(n,o)=>{e.push(`${encodeURIComponent(n)}=${encodeURIComponent(String(o))}`)},s=(n,o)=>{Qe(o)&&(Array.isArray(o)?o.forEach(i=>{s(n,i)}):typeof o=="object"?Object.entries(o).forEach(([i,a])=>{s(`${n}[${i}]`,a)}):r(n,o))};return Object.entries(t).forEach(([n,o])=>{s(n,o)}),e.length>0?`?${e.join("&")}`:""},ui=(t,e)=>{const r=t.ENCODE_PATH||encodeURI,s=e.url.replace("{api-version}",t.VERSION).replace(/{(.*?)}/g,(o,i)=>{var a;return(a=e.path)!=null&&a.hasOwnProperty(i)?r(String(e.path[i])):o}),n=`${t.BASE}${s}`;return e.query?`${n}${li(e.query)}`:n},di=t=>{if(t.formData){const e=new FormData,r=(s,n)=>{ce(n)||Xe(n)?e.append(s,n):e.append(s,JSON.stringify(n))};return Object.entries(t.formData).filter(([s,n])=>Qe(n)).forEach(([s,n])=>{Array.isArray(n)?n.forEach(o=>r(s,o)):r(s,n)}),e}},de=async(t,e)=>typeof e=="function"?e(t):e,hi=async(t,e)=>{const r=await de(e,t.TOKEN),s=await de(e,t.USERNAME),n=await de(e,t.PASSWORD),o=await de(e,t.HEADERS),i=Object.entries({Accept:"application/json",...o,...e.headers}).filter(([a,c])=>Qe(c)).reduce((a,[c,l])=>({...a,[c]:String(l)}),{});if(Ae(r)&&(i.Authorization=`Bearer ${r}`),Ae(s)&&Ae(n)){const a=ci(`${s}:${n}`);i.Authorization=`Basic ${a}`}return e.body&&(e.mediaType?i["Content-Type"]=e.mediaType:Xe(e.body)?i["Content-Type"]=e.body.type||"application/octet-stream":ce(e.body)?i["Content-Type"]="text/plain":ur(e.body)||(i["Content-Type"]="application/json")),new Headers(i)},pi=t=>{var e;if(t.body)return(e=t.mediaType)!=null&&e.includes("/json")?JSON.stringify(t.body):ce(t.body)||Xe(t.body)||ur(t.body)?t.body:JSON.stringify(t.body)},fi=(t,e,r,s,n,o,i)=>{const a=new AbortController,c={headers:o,body:s??n,method:e.method,signal:a.signal};return t.WITH_CREDENTIALS&&(c.credentials=t.CREDENTIALS),i(()=>a.abort()),fetch(r,c)},mi=(t,e)=>{if(e){const r=t.headers.get(e);if(ce(r))return r}},bi=async t=>{if(t.status!==204)try{const e=t.headers.get("Content-Type");if(e){const r=e.toLowerCase(),s=r.startsWith("application/json"),n=["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet","application/vnd.ms-excel","text/csv"].some(o=>r.includes(o));return s?await t.json():n?await t.blob():await t.text()}}catch(e){console.error(e)}},gi=(t,e)=>{const s={400:"Bad Request",401:"Unauthorized",403:"Forbidden",404:"Not Found",500:"Internal Server Error",502:"Bad Gateway",503:"Service Unavailable",...t.errors}[e.status];if(e.status===503){window.location.assign(Be);return}if(s)throw new Le(t,e,s);if(!e.ok)throw new Le(t,e,"Generic Error")},Ei=(t,e)=>new ai(async(r,s,n)=>{try{const o=ui(t,e),i=di(e),a=pi(e),c=await hi(t,e);if(!n.isCancelled){const l=await fi(t,e,o,a,i,c,n),d=await bi(l),p=mi(l,e.responseHeader),f={url:o,ok:l.ok,status:l.status,statusText:l.statusText,body:p??d};gi(e,f),r(f.body)}}catch(o){if(o instanceof Le&&o.status===401){if(o.url.includes("/adage-iframe")){window.location.href="/adage-iframe/erreur";return}if(!o.url.includes("/users/current")&&!o.url.includes("/users/signin")){window.location.href="/connexion";return}}s(o)}});class yi extends oi{constructor(e){super(e)}request(e){return Ei(this.config,e)}}class Ti{constructor(e){this.httpRequest=e}cancelCollectiveBooking(e){return this.httpRequest.request({method:"PATCH",url:"/v2/collective/bookings/{booking_id}",path:{booking_id:e},errors:{401:"Authentification nécessaire",422:"Unprocessable Entity"}})}listCategories(){return this.httpRequest.request({method:"GET",url:"/v2/collective/categories",errors:{401:"Authentification nécessaire",422:"Unprocessable Entity"}})}listEducationalDomains(){return this.httpRequest.request({method:"GET",url:"/v2/collective/educational-domains",errors:{401:"Authentification nécessaire",422:"Unprocessable Entity"}})}listEducationalInstitutions(e,r,s,n,o,i,a=20){return this.httpRequest.request({method:"GET",url:"/v2/collective/educational-institutions/",query:{id:e,name:r,institutionType:s,city:n,postalCode:o,uai:i,limit:a},errors:{400:"Requête malformée",401:"Authentification nécessaire",422:"Unprocessable Entity"}})}getNationalPrograms(){return this.httpRequest.request({method:"GET",url:"/v2/collective/national-programs/",errors:{401:"Authentification nécessaire",403:"Vous n'avez pas les droits nécessaires pour voir ces informations",422:"Unprocessable Entity"}})}getOffererVenues(e){return this.httpRequest.request({method:"GET",url:"/v2/collective/offerer_venues",query:{siren:e},errors:{401:"Authentification nécessaire",422:"Unprocessable Entity"}})}getCollectiveOffersPublic(e,r,s,n){return this.httpRequest.request({method:"GET",url:"/v2/collective/offers/",query:{status:e,venueId:r,periodBeginningDate:s,periodEndingDate:n},errors:{401:"Authentification nécessaire",403:"Vous n'avez pas les droits nécessaires pour voir cette offre collective",404:"L'offre collective n'existe pas",422:"Unprocessable Entity"}})}postCollectiveOfferPublic(e){return this.httpRequest.request({method:"POST",url:"/v2/collective/offers/",body:e,mediaType:"application/json",errors:{400:"Requête malformée",401:"Authentification nécessaire",403:"Non éligible pour les offres collectives",404:"L'une des resources pour la création de l'offre n'a pas été trouvée",422:"Unprocessable Entity"}})}getOffersFormats(){return this.httpRequest.request({method:"GET",url:"/v2/collective/offers/formats",errors:{401:"Authentification nécessaire",403:"Vous n'avez pas les droits nécessaires pour voir cette offre collective",404:"L'offre collective n'existe pas",422:"Unprocessable Entity"}})}getCollectiveOfferPublic(e){return this.httpRequest.request({method:"GET",url:"/v2/collective/offers/{offer_id}",path:{offer_id:e},errors:{401:"Authentification nécessaire",403:"Vous n'avez pas les droits nécessaires pour voir cette offre collective",404:"L'offre collective n'existe pas",422:"Unprocessable Entity"}})}patchCollectiveOfferPublic(e,r){return this.httpRequest.request({method:"PATCH",url:"/v2/collective/offers/{offer_id}",path:{offer_id:e},body:r,mediaType:"application/json",errors:{400:"Requête malformée",401:"Authentification nécessaire",403:"Vous n'avez pas les droits nécessaires pour éditer cette offre collective",404:"L'une des resources pour la création de l'offre n'a pas été trouvée",422:"Cetains champs ne peuvent pas être édités selon l'état de l'offre"}})}listStudentsLevels(){return this.httpRequest.request({method:"GET",url:"/v2/collective/student-levels",errors:{401:"Authentification nécessaire",422:"Unprocessable Entity"}})}listSubcategories(){return this.httpRequest.request({method:"GET",url:"/v2/collective/subcategories",errors:{401:"Authentification nécessaire",422:"Unprocessable Entity"}})}listVenues(){return this.httpRequest.request({method:"GET",url:"/v2/collective/venues",errors:{401:"Authentification nécessaire",422:"Unprocessable Entity"}})}}class _i{constructor(e){this.httpRequest=e}patchCancelBookingByToken(e){return this.httpRequest.request({method:"PATCH",url:"/v2/bookings/cancel/token/{token}",path:{token:e},errors:{401:"Authentification nécessaire",403:"Vous n'avez pas les droits nécessaires pour annuler cette contremarque ou la réservation a déjà été validée",404:"La contremarque n'existe pas",410:"La contremarque a déjà été annulée",422:"Unprocessable Entity"}})}patchBookingKeepByToken(e){return this.httpRequest.request({method:"PATCH",url:"/v2/bookings/keep/token/{token}",path:{token:e},errors:{401:"Authentification nécessaire",403:"Vous n'avez pas les droits nécessaires pour voir cette contremarque",404:"La contremarque n'existe pas",410:"La requête est refusée car la contremarque n'a pas encore été validée, a été annulée, ou son remboursement a été initié",422:"Unprocessable Entity"}})}getBookingByTokenV2(e){return this.httpRequest.request({method:"GET",url:"/v2/bookings/token/{token}",path:{token:e},errors:{401:"Authentification nécessaire",403:"Vous n'avez pas les droits nécessaires pour voir cette contremarque",404:"La contremarque n'existe pas",410:`Cette contremarque a été validée.
        En l’invalidant vous indiquez qu’elle n’a pas été utilisée et vous ne serez pas remboursé.`,422:"Unprocessable Entity"}})}patchBookingUseByToken(e){return this.httpRequest.request({method:"PATCH",url:"/v2/bookings/use/token/{token}",path:{token:e},errors:{401:"Authentification nécessaire",403:"Vous n'avez pas les droits nécessaires pour voir cette contremarque",404:"La contremarque n'existe pas",410:`Cette contremarque a été validée.
        En l’invalidant vous indiquez qu’elle n’a pas été utilisée et vous ne serez pas remboursé.`,422:"Unprocessable Entity"}})}}class Ci{constructor(e,r=yi){this.request=new r({BASE:(e==null?void 0:e.BASE)??"http://localhost:5001",VERSION:(e==null?void 0:e.VERSION)??"2",WITH_CREDENTIALS:(e==null?void 0:e.WITH_CREDENTIALS)??!1,CREDENTIALS:(e==null?void 0:e.CREDENTIALS)??"include",TOKEN:e==null?void 0:e.TOKEN,USERNAME:e==null?void 0:e.USERNAME,PASSWORD:e==null?void 0:e.PASSWORD,HEADERS:e==null?void 0:e.HEADERS,ENCODE_PATH:e==null?void 0:e.ENCODE_PATH}),this.apiOffresCollectives=new Ti(this.request),this.dPrCiEApiContremarque=new _i(this.request)}}const Ri=new URLSearchParams(window.location.search),Si=Ri.get("token"),dr={BASE:qt,VERSION:"1",WITH_CREDENTIALS:!0,CREDENTIALS:"include"},Ii={BASE:qt,VERSION:"1",WITH_CREDENTIALS:!1,CREDENTIALS:"omit",TOKEN:Si??""};new Pr(dr).default;new Ci(dr).dPrCiEApiContremarque;new ni(Ii).default;const qi=t=>Object.fromEntries(new URLSearchParams(t)),wi=()=>{const t=fr(),e=qi(t.search);return"utm_campaign"in e&&"utm_medium"in e&&"utm_source"in e?{traffic_campaign:e.utm_campaign,traffic_medium:e.utm_medium,traffic_source:e.utm_source}:{}},Ai=()=>{const t=wi();return{logEvent:pr.useCallback((r,s)=>{},[t])}};var hr=(t=>(t.CLICKED_BOOKING="hasClickedBooking",t.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",t.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",t.CLICKED_CONSULT_CGU="hasClickedConsultCGU",t.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",t.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",t.CLICKED_CREATE_VENUE="hasClickedCreateVenue",t.CLICKED_ADD_BANK_INFORMATIONS="hasClickedAddBankInformation",t.CLICKED_NO_PRICING_POINT_SELECTED_YET="hasClickedNoPricingPointSelectedYet",t.CLICKED_ADD_VENUE_IN_OFFERER="hasClickedAddVenueInOfferer",t.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",t.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",t.CLICKED_SAVE_VENUE="hasClickedSaveVenue",t.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",t.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",t.CLICKED_DOWNLOAD_BOOKINGS_OTHER_FORMAT="hasClickedDownloadBookingOtherFormat",t.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",t.CLICKED_EDIT_PROFILE="hasClickedEditProfile",t.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",t.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",t.CLICKED_HELP_CENTER="hasClickedHelpCenter",t.CLICKED_HOME="hasClickedHome",t.CLICKED_LOGOUT="hasClickedLogout",t.CLICKED_MODIFY_OFFERER="hasClickedModifyOfferer",t.CLICKED_OFFER="hasClickedOffer",t.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",t.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",t.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",t.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",t.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",t.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",t.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",t.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",t.CLICKED_PRO="hasClickedPro",t.CLICKED_REIMBURSEMENT="hasClickedReimbursement",t.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",t.CLICKED_STATS="hasClickedOffererStats",t.CLICKED_TICKET="hasClickedTicket",t.CLICKED_TOGGLE_HIDE_OFFERER_NAME="hasClickedToggleHideOffererName",t.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",t.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",t.CLICKED_HELP_LINK="hasClickedHelpLink",t.CLICKED_RESET_FILTERS="hasClickedResetFilter",t.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",t.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",t.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",t.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",t.FIRST_LOGIN="firstLogin",t.PAGE_VIEW="page_view",t.SIGNUP_FORM_ABORT="signupFormAbort",t.SIGNUP_FORM_SUCCESS="signupFormSuccess",t.TUTO_PAGE_VIEW="tutoPageView",t.DELETE_DRAFT_OFFER="DeleteDraftOffer",t.CLICKED_NO_VENUE="hasClickedNoVenue",t.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",t.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",t.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",t.CLICKED_ADD_IMAGE="hasClickedAddImage",t.CLICKED_DELETE_STOCK="hasClickedDeleteStock",t.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",t.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",t))(hr||{});const Tt={"help-link":"_help-link_1c4y5_2","help-link-text":"_help-link-text_1c4y5_10"},vi=()=>{const{logEvent:t}=Ai();return re.jsxs("a",{onClick:()=>t(hr.CLICKED_HELP_LINK,{from:location.pathname}),className:Tt["help-link"],href:"https://aide.passculture.app/hc/fr/articles/4411991940369--Acteurs-culturels-Comment-poster-une-offre-%C3%A0-destination-d-un-groupe-scolaire-",rel:"noreferrer",target:"_blank",children:[re.jsx(br,{src:mr,alt:"",width:"42"}),re.jsx("span",{className:Tt["help-link-text"],children:"Aide"})]})},Zi={title:"components/HelpLink",component:vi,decorators:[t=>re.jsx("div",{style:{width:500,height:500},children:re.jsx(t,{})})]},he={};var Rt,St,It;he.parameters={...he.parameters,docs:{...(Rt=he.parameters)==null?void 0:Rt.docs,source:{originalSource:"{}",...(It=(St=he.parameters)==null?void 0:St.docs)==null?void 0:It.source}}};const ea=["Default"];export{he as Default,ea as __namedExportsOrder,Zi as default};
