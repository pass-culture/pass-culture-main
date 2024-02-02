import{j as O}from"./jsx-runtime-iXOPPpZ7.js";import{r as N}from"./index-7OBYoplD.js";import"./config-KjRYmNhP.js";import{f as un}from"./full-help-eUK0ZyWO.js";import{S as dn}from"./SvgIcon-UUSKXfrA.js";import"./_commonjsHelpers-4gQjN7DL.js";var lt=(e=>(e.CLICKED_BOOKING="hasClickedBooking",e.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",e.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",e.CLICKED_CONSULT_CGU="hasClickedConsultCGU",e.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",e.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",e.CLICKED_CREATE_VENUE="hasClickedCreateVenue",e.CLICKED_ADD_BANK_INFORMATIONS="hasClickedAddBankInformation",e.CLICKED_NO_PRICING_POINT_SELECTED_YET="hasClickedNoPricingPointSelectedYet",e.CLICKED_ADD_VENUE_IN_OFFERER="hasClickedAddVenueInOfferer",e.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",e.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",e.CLICKED_SAVE_VENUE="hasClickedSaveVenue",e.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",e.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",e.CLICKED_DOWNLOAD_BOOKINGS_OTHER_FORMAT="hasClickedDownloadBookingOtherFormat",e.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",e.CLICKED_EDIT_PROFILE="hasClickedEditProfile",e.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",e.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",e.CLICKED_HELP_CENTER="hasClickedHelpCenter",e.CLICKED_HOME="hasClickedHome",e.CLICKED_LOGOUT="hasClickedLogout",e.CLICKED_MODIFY_OFFERER="hasClickedModifyOfferer",e.CLICKED_OFFER="hasClickedOffer",e.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",e.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",e.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",e.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",e.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",e.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",e.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",e.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",e.CLICKED_PRO="hasClickedPro",e.CLICKED_REIMBURSEMENT="hasClickedReimbursement",e.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",e.CLICKED_STATS="hasClickedOffererStats",e.CLICKED_TICKET="hasClickedTicket",e.CLICKED_TOGGLE_HIDE_OFFERER_NAME="hasClickedToggleHideOffererName",e.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",e.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",e.CLICKED_HELP_LINK="hasClickedHelpLink",e.CLICKED_RESET_FILTERS="hasClickedResetFilter",e.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",e.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",e.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",e.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",e.FIRST_LOGIN="firstLogin",e.PAGE_VIEW="page_view",e.SIGNUP_FORM_ABORT="signupFormAbort",e.SIGNUP_FORM_SUCCESS="signupFormSuccess",e.TUTO_PAGE_VIEW="tutoPageView",e.DELETE_DRAFT_OFFER="DeleteDraftOffer",e.CLICKED_NO_VENUE="hasClickedNoVenue",e.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",e.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",e.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",e.CLICKED_ADD_IMAGE="hasClickedAddImage",e.CLICKED_DELETE_STOCK="hasClickedDeleteStock",e.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",e))(lt||{});/**
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
 */const ut=function(e){const t=[];let n=0;for(let r=0;r<e.length;r++){let a=e.charCodeAt(r);a<128?t[n++]=a:a<2048?(t[n++]=a>>6|192,t[n++]=a&63|128):(a&64512)===55296&&r+1<e.length&&(e.charCodeAt(r+1)&64512)===56320?(a=65536+((a&1023)<<10)+(e.charCodeAt(++r)&1023),t[n++]=a>>18|240,t[n++]=a>>12&63|128,t[n++]=a>>6&63|128,t[n++]=a&63|128):(t[n++]=a>>12|224,t[n++]=a>>6&63|128,t[n++]=a&63|128)}return t},hn=function(e){const t=[];let n=0,r=0;for(;n<e.length;){const a=e[n++];if(a<128)t[r++]=String.fromCharCode(a);else if(a>191&&a<224){const s=e[n++];t[r++]=String.fromCharCode((a&31)<<6|s&63)}else if(a>239&&a<365){const s=e[n++],o=e[n++],i=e[n++],c=((a&7)<<18|(s&63)<<12|(o&63)<<6|i&63)-65536;t[r++]=String.fromCharCode(55296+(c>>10)),t[r++]=String.fromCharCode(56320+(c&1023))}else{const s=e[n++],o=e[n++];t[r++]=String.fromCharCode((a&15)<<12|(s&63)<<6|o&63)}}return t.join("")},fn={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,r=[];for(let a=0;a<e.length;a+=3){const s=e[a],o=a+1<e.length,i=o?e[a+1]:0,c=a+2<e.length,l=c?e[a+2]:0,u=s>>2,h=(s&3)<<4|i>>4;let f=(i&15)<<2|l>>6,g=l&63;c||(g=64,o||(f=64)),r.push(n[u],n[h],n[f],n[g])}return r.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(ut(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):hn(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const n=t?this.charToByteMapWebSafe_:this.charToByteMap_,r=[];for(let a=0;a<e.length;){const s=n[e.charAt(a++)],i=a<e.length?n[e.charAt(a)]:0;++a;const l=a<e.length?n[e.charAt(a)]:64;++a;const h=a<e.length?n[e.charAt(a)]:64;if(++a,s==null||i==null||l==null||h==null)throw new gn;const f=s<<2|i>>4;if(r.push(f),l!==64){const g=i<<4&240|l>>2;if(r.push(g),h!==64){const E=l<<6&192|h;r.push(E)}}}return r},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class gn extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const pn=function(e){const t=ut(e);return fn.encodeByteArray(t,!0)},dt=function(e){return pn(e).replace(/\./g,"")};function mn(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function ht(){try{return typeof indexedDB=="object"}catch{return!1}}function ft(){return new Promise((e,t)=>{try{let n=!0;const r="validate-browser-context-for-indexeddb-analytics-module",a=self.indexedDB.open(r);a.onsuccess=()=>{a.result.close(),n||self.indexedDB.deleteDatabase(r),e(!0)},a.onupgradeneeded=()=>{n=!1},a.onerror=()=>{var s;t(((s=a.error)===null||s===void 0?void 0:s.message)||"")}}catch(n){t(n)}})}function Cn(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const In="FirebaseError";let x=class gt extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=In,Object.setPrototypeOf(this,gt.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,q.prototype.create)}},q=class{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},a=`${this.service}/${t}`,s=this.errors[t],o=s?_n(s,r):"Error",i=`${this.serviceName}: ${o} (${a}).`;return new x(a,i,r)}};function _n(e,t){return e.replace(bn,(n,r)=>{const a=t[r];return a!=null?String(a):`<${r}?>`})}const bn=/\{\$([^}]+)}/g;/**
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
 */const En=1e3,wn=2,yn=4*60*60*1e3,Tn=.5;function Me(e,t=En,n=wn){const r=t*Math.pow(n,e),a=Math.round(Tn*r*(Math.random()-.5)*2);return Math.min(yn,r+a)}/**
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
 */function Sn(e){return e&&e._delegate?e._delegate:e}let R=class{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}};/**
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
 */var d;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(d||(d={}));const An={debug:d.DEBUG,verbose:d.VERBOSE,info:d.INFO,warn:d.WARN,error:d.ERROR,silent:d.SILENT},Dn=d.INFO,On={[d.DEBUG]:"log",[d.VERBOSE]:"log",[d.INFO]:"info",[d.WARN]:"warn",[d.ERROR]:"error"},Rn=(e,t,...n)=>{if(t<e.logLevel)return;const r=new Date().toISOString(),a=On[t];if(a)console[a](`[${r}]  ${e.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class Ie{constructor(t){this.name=t,this._logLevel=Dn,this._logHandler=Rn,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in d))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?An[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,d.DEBUG,...t),this._logHandler(this,d.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,d.VERBOSE,...t),this._logHandler(this,d.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,d.INFO,...t),this._logHandler(this,d.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,d.WARN,...t),this._logHandler(this,d.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,d.ERROR,...t),this._logHandler(this,d.ERROR,...t)}}const Ln=(e,t)=>t.some(n=>e instanceof n);let Pe,Ne;function $n(){return Pe||(Pe=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function kn(){return Ne||(Ne=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const pt=new WeakMap,ue=new WeakMap,mt=new WeakMap,X=new WeakMap,_e=new WeakMap;function Mn(e){const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("success",s),e.removeEventListener("error",o)},s=()=>{n(y(e.result)),a()},o=()=>{r(e.error),a()};e.addEventListener("success",s),e.addEventListener("error",o)});return t.then(n=>{n instanceof IDBCursor&&pt.set(n,e)}).catch(()=>{}),_e.set(t,e),t}function Pn(e){if(ue.has(e))return;const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("complete",s),e.removeEventListener("error",o),e.removeEventListener("abort",o)},s=()=>{n(),a()},o=()=>{r(e.error||new DOMException("AbortError","AbortError")),a()};e.addEventListener("complete",s),e.addEventListener("error",o),e.addEventListener("abort",o)});ue.set(e,t)}let de={get(e,t,n){if(e instanceof IDBTransaction){if(t==="done")return ue.get(e);if(t==="objectStoreNames")return e.objectStoreNames||mt.get(e);if(t==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return y(e[t])},set(e,t,n){return e[t]=n,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function Nn(e){de=e(de)}function Fn(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...n){const r=e.call(Q(this),t,...n);return mt.set(r,t.sort?t.sort():[t]),y(r)}:kn().includes(e)?function(...t){return e.apply(Q(this),t),y(pt.get(this))}:function(...t){return y(e.apply(Q(this),t))}}function vn(e){return typeof e=="function"?Fn(e):(e instanceof IDBTransaction&&Pn(e),Ln(e,$n())?new Proxy(e,de):e)}function y(e){if(e instanceof IDBRequest)return Mn(e);if(X.has(e))return X.get(e);const t=vn(e);return t!==e&&(X.set(e,t),_e.set(t,e)),t}const Q=e=>_e.get(e);function Ct(e,t,{blocked:n,upgrade:r,blocking:a,terminated:s}={}){const o=indexedDB.open(e,t),i=y(o);return r&&o.addEventListener("upgradeneeded",c=>{r(y(o.result),c.oldVersion,c.newVersion,y(o.transaction),c)}),n&&o.addEventListener("blocked",c=>n(c.oldVersion,c.newVersion,c)),i.then(c=>{s&&c.addEventListener("close",()=>s()),a&&c.addEventListener("versionchange",l=>a(l.oldVersion,l.newVersion,l))}).catch(()=>{}),i}const Bn=["get","getKey","getAll","getAllKeys","count"],xn=["put","add","delete","clear"],Z=new Map;function Fe(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(Z.get(t))return Z.get(t);const n=t.replace(/FromIndex$/,""),r=t!==n,a=xn.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(a||Bn.includes(n)))return;const s=async function(o,...i){const c=this.transaction(o,a?"readwrite":"readonly");let l=c.store;return r&&(l=l.index(i.shift())),(await Promise.all([l[n](...i),a&&c.done]))[0]};return Z.set(t,s),s}Nn(e=>({...e,get:(t,n,r)=>Fe(t,n)||e.get(t,n,r),has:(t,n)=>!!Fe(t,n)||e.has(t,n)}));/**
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
 */class Kn{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(jn(n)){const r=n.getImmediate();return`${r.library}/${r.version}`}else return null}).filter(n=>n).join(" ")}}function jn(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const he="@firebase/app",ve="0.9.26";/**
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
 */const L=new Ie("@firebase/app"),Vn="@firebase/app-compat",Hn="@firebase/analytics-compat",Un="@firebase/analytics",qn="@firebase/app-check-compat",Gn="@firebase/app-check",Wn="@firebase/auth",zn="@firebase/auth-compat",Yn="@firebase/database",Jn="@firebase/database-compat",Xn="@firebase/functions",Qn="@firebase/functions-compat",Zn="@firebase/installations",er="@firebase/installations-compat",tr="@firebase/messaging",nr="@firebase/messaging-compat",rr="@firebase/performance",ar="@firebase/performance-compat",sr="@firebase/remote-config",or="@firebase/remote-config-compat",ir="@firebase/storage",cr="@firebase/storage-compat",lr="@firebase/firestore",ur="@firebase/firestore-compat",dr="firebase",hr="10.7.2",fr={[he]:"fire-core",[Vn]:"fire-core-compat",[Un]:"fire-analytics",[Hn]:"fire-analytics-compat",[Gn]:"fire-app-check",[qn]:"fire-app-check-compat",[Wn]:"fire-auth",[zn]:"fire-auth-compat",[Yn]:"fire-rtdb",[Jn]:"fire-rtdb-compat",[Xn]:"fire-fn",[Qn]:"fire-fn-compat",[Zn]:"fire-iid",[er]:"fire-iid-compat",[tr]:"fire-fcm",[nr]:"fire-fcm-compat",[rr]:"fire-perf",[ar]:"fire-perf-compat",[sr]:"fire-rc",[or]:"fire-rc-compat",[ir]:"fire-gcs",[cr]:"fire-gcs-compat",[lr]:"fire-fst",[ur]:"fire-fst-compat","fire-js":"fire-js",[dr]:"fire-js-all"};/**
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
 */const gr=new Map,Be=new Map;function pr(e,t){try{e.container.addComponent(t)}catch(n){L.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,n)}}function b(e){const t=e.name;if(Be.has(t))return L.debug(`There were multiple attempts to register component ${t}.`),!1;Be.set(t,e);for(const n of gr.values())pr(n,e);return!0}function G(e,t){const n=e.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),e.container.getProvider(t)}/**
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
 */const mr={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}."},be=new q("app","Firebase",mr);/**
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
 */const Cr=hr;function _(e,t,n){var r;let a=(r=fr[e])!==null&&r!==void 0?r:e;n&&(a+=`-${n}`);const s=a.match(/\s|\//),o=t.match(/\s|\//);if(s||o){const i=[`Unable to register library "${a}" with version "${t}":`];s&&i.push(`library name "${a}" contains illegal characters (whitespace or "/")`),s&&o&&i.push("and"),o&&i.push(`version name "${t}" contains illegal characters (whitespace or "/")`),L.warn(i.join(" "));return}b(new R(`${a}-version`,()=>({library:a,version:t}),"VERSION"))}/**
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
 */const Ir="firebase-heartbeat-database",_r=1,B="firebase-heartbeat-store";let ee=null;function It(){return ee||(ee=Ct(Ir,_r,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(B)}catch(n){console.warn(n)}}}}).catch(e=>{throw be.create("idb-open",{originalErrorMessage:e.message})})),ee}async function br(e){try{return await(await It()).transaction(B).objectStore(B).get(_t(e))}catch(t){if(t instanceof x)L.warn(t.message);else{const n=be.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});L.warn(n.message)}}}async function xe(e,t){try{const r=(await It()).transaction(B,"readwrite");await r.objectStore(B).put(t,_t(e)),await r.done}catch(n){if(n instanceof x)L.warn(n.message);else{const r=be.create("idb-set",{originalErrorMessage:n==null?void 0:n.message});L.warn(r.message)}}}function _t(e){return`${e.name}!${e.options.appId}`}/**
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
 */const Er=1024,wr=30*24*60*60*1e3;class yr{constructor(t){this.container=t,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new Sr(n),this._heartbeatsCachePromise=this._storage.read().then(r=>(this._heartbeatsCache=r,r))}async triggerHeartbeat(){var t,n;const a=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),s=Ke();if(!(((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((n=this._heartbeatsCache)===null||n===void 0?void 0:n.heartbeats)==null))&&!(this._heartbeatsCache.lastSentHeartbeatDate===s||this._heartbeatsCache.heartbeats.some(o=>o.date===s)))return this._heartbeatsCache.heartbeats.push({date:s,agent:a}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(o=>{const i=new Date(o.date).valueOf();return Date.now()-i<=wr}),this._storage.overwrite(this._heartbeatsCache)}async getHeartbeatsHeader(){var t;if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const n=Ke(),{heartbeatsToSend:r,unsentEntries:a}=Tr(this._heartbeatsCache.heartbeats),s=dt(JSON.stringify({version:2,heartbeats:r}));return this._heartbeatsCache.lastSentHeartbeatDate=n,a.length>0?(this._heartbeatsCache.heartbeats=a,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}}function Ke(){return new Date().toISOString().substring(0,10)}function Tr(e,t=Er){const n=[];let r=e.slice();for(const a of e){const s=n.find(o=>o.agent===a.agent);if(s){if(s.dates.push(a.date),je(n)>t){s.dates.pop();break}}else if(n.push({agent:a.agent,dates:[a.date]}),je(n)>t){n.pop();break}r=r.slice(1)}return{heartbeatsToSend:n,unsentEntries:r}}class Sr{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return ht()?ft().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const n=await br(this.app);return n!=null&&n.heartbeats?n:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){var n;if(await this._canUseIndexedDBPromise){const a=await this.read();return xe(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:a.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){var n;if(await this._canUseIndexedDBPromise){const a=await this.read();return xe(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:a.lastSentHeartbeatDate,heartbeats:[...a.heartbeats,...t.heartbeats]})}else return}}function je(e){return dt(JSON.stringify({version:2,heartbeats:e})).length}/**
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
 */function Ar(e){b(new R("platform-logger",t=>new Kn(t),"PRIVATE")),b(new R("heartbeat",t=>new yr(t),"PRIVATE")),_(he,ve,e),_(he,ve,"esm2017"),_("fire-js","")}Ar("");const Dr=(e,t)=>t.some(n=>e instanceof n);let Ve,He;function Or(){return Ve||(Ve=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Rr(){return He||(He=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const bt=new WeakMap,fe=new WeakMap,Et=new WeakMap,te=new WeakMap,Ee=new WeakMap;function Lr(e){const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("success",s),e.removeEventListener("error",o)},s=()=>{n(T(e.result)),a()},o=()=>{r(e.error),a()};e.addEventListener("success",s),e.addEventListener("error",o)});return t.then(n=>{n instanceof IDBCursor&&bt.set(n,e)}).catch(()=>{}),Ee.set(t,e),t}function $r(e){if(fe.has(e))return;const t=new Promise((n,r)=>{const a=()=>{e.removeEventListener("complete",s),e.removeEventListener("error",o),e.removeEventListener("abort",o)},s=()=>{n(),a()},o=()=>{r(e.error||new DOMException("AbortError","AbortError")),a()};e.addEventListener("complete",s),e.addEventListener("error",o),e.addEventListener("abort",o)});fe.set(e,t)}let ge={get(e,t,n){if(e instanceof IDBTransaction){if(t==="done")return fe.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Et.get(e);if(t==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return T(e[t])},set(e,t,n){return e[t]=n,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function kr(e){ge=e(ge)}function Mr(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...n){const r=e.call(ne(this),t,...n);return Et.set(r,t.sort?t.sort():[t]),T(r)}:Rr().includes(e)?function(...t){return e.apply(ne(this),t),T(bt.get(this))}:function(...t){return T(e.apply(ne(this),t))}}function Pr(e){return typeof e=="function"?Mr(e):(e instanceof IDBTransaction&&$r(e),Dr(e,Or())?new Proxy(e,ge):e)}function T(e){if(e instanceof IDBRequest)return Lr(e);if(te.has(e))return te.get(e);const t=Pr(e);return t!==e&&(te.set(e,t),Ee.set(t,e)),t}const ne=e=>Ee.get(e);function Nr(e,t,{blocked:n,upgrade:r,blocking:a,terminated:s}={}){const o=indexedDB.open(e,t),i=T(o);return r&&o.addEventListener("upgradeneeded",c=>{r(T(o.result),c.oldVersion,c.newVersion,T(o.transaction))}),n&&o.addEventListener("blocked",()=>n()),i.then(c=>{s&&c.addEventListener("close",()=>s()),a&&c.addEventListener("versionchange",()=>a())}).catch(()=>{}),i}const Fr=["get","getKey","getAll","getAllKeys","count"],vr=["put","add","delete","clear"],re=new Map;function Ue(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(re.get(t))return re.get(t);const n=t.replace(/FromIndex$/,""),r=t!==n,a=vr.includes(n);if(!(n in(r?IDBIndex:IDBObjectStore).prototype)||!(a||Fr.includes(n)))return;const s=async function(o,...i){const c=this.transaction(o,a?"readwrite":"readonly");let l=c.store;return r&&(l=l.index(i.shift())),(await Promise.all([l[n](...i),a&&c.done]))[0]};return re.set(t,s),s}kr(e=>({...e,get:(t,n,r)=>Ue(t,n)||e.get(t,n,r),has:(t,n)=>!!Ue(t,n)||e.has(t,n)}));const wt="@firebase/installations",we="0.6.4";/**
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
 */const yt=1e4,Tt=`w:${we}`,St="FIS_v2",Br="https://firebaseinstallations.googleapis.com/v1",xr=60*60*1e3,Kr="installations",jr="Installations";/**
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
 */const Vr={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},$=new q(Kr,jr,Vr);function At(e){return e instanceof x&&e.code.includes("request-failed")}/**
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
 */function Dt({projectId:e}){return`${Br}/projects/${e}/installations`}function Ot(e){return{token:e.token,requestStatus:2,expiresIn:Ur(e.expiresIn),creationTime:Date.now()}}async function Rt(e,t){const r=(await t.json()).error;return $.create("request-failed",{requestName:e,serverCode:r.code,serverMessage:r.message,serverStatus:r.status})}function Lt({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Hr(e,{refreshToken:t}){const n=Lt(e);return n.append("Authorization",qr(t)),n}async function $t(e){const t=await e();return t.status>=500&&t.status<600?e():t}function Ur(e){return Number(e.replace("s","000"))}function qr(e){return`${St} ${e}`}/**
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
 */async function Gr({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const r=Dt(e),a=Lt(e),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const o={fid:n,authVersion:St,appId:e.appId,sdkVersion:Tt},i={method:"POST",headers:a,body:JSON.stringify(o)},c=await $t(()=>fetch(r,i));if(c.ok){const l=await c.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:Ot(l.authToken)}}else throw await Rt("Create Installation",c)}/**
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
 */function kt(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function Wr(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const zr=/^[cdef][\w-]{21}$/,pe="";function Yr(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=Jr(e);return zr.test(n)?n:pe}catch{return pe}}function Jr(e){return Wr(e).substr(0,22)}/**
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
 */function W(e){return`${e.appName}!${e.appId}`}/**
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
 */const Mt=new Map;function Pt(e,t){const n=W(e);Nt(n,t),Xr(n,t)}function Nt(e,t){const n=Mt.get(e);if(n)for(const r of n)r(t)}function Xr(e,t){const n=Qr();n&&n.postMessage({key:e,fid:t}),Zr()}let A=null;function Qr(){return!A&&"BroadcastChannel"in self&&(A=new BroadcastChannel("[Firebase] FID Change"),A.onmessage=e=>{Nt(e.data.key,e.data.fid)}),A}function Zr(){Mt.size===0&&A&&(A.close(),A=null)}/**
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
 */const ea="firebase-installations-database",ta=1,k="firebase-installations-store";let ae=null;function ye(){return ae||(ae=Nr(ea,ta,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(k)}}})),ae}async function H(e,t){const n=W(e),a=(await ye()).transaction(k,"readwrite"),s=a.objectStore(k),o=await s.get(n);return await s.put(t,n),await a.done,(!o||o.fid!==t.fid)&&Pt(e,t.fid),t}async function Ft(e){const t=W(e),r=(await ye()).transaction(k,"readwrite");await r.objectStore(k).delete(t),await r.done}async function z(e,t){const n=W(e),a=(await ye()).transaction(k,"readwrite"),s=a.objectStore(k),o=await s.get(n),i=t(o);return i===void 0?await s.delete(n):await s.put(i,n),await a.done,i&&(!o||o.fid!==i.fid)&&Pt(e,i.fid),i}/**
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
 */async function Te(e){let t;const n=await z(e.appConfig,r=>{const a=na(r),s=ra(e,a);return t=s.registrationPromise,s.installationEntry});return n.fid===pe?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function na(e){const t=e||{fid:Yr(),registrationStatus:0};return vt(t)}function ra(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const a=Promise.reject($.create("app-offline"));return{installationEntry:t,registrationPromise:a}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},r=aa(e,n);return{installationEntry:n,registrationPromise:r}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:sa(e)}:{installationEntry:t}}async function aa(e,t){try{const n=await Gr(e,t);return H(e.appConfig,n)}catch(n){throw At(n)&&n.customData.serverCode===409?await Ft(e.appConfig):await H(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function sa(e){let t=await qe(e.appConfig);for(;t.registrationStatus===1;)await kt(100),t=await qe(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:r}=await Te(e);return r||n}return t}function qe(e){return z(e,t=>{if(!t)throw $.create("installation-not-found");return vt(t)})}function vt(e){return oa(e)?{fid:e.fid,registrationStatus:0}:e}function oa(e){return e.registrationStatus===1&&e.registrationTime+yt<Date.now()}/**
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
 */async function ia({appConfig:e,heartbeatServiceProvider:t},n){const r=ca(e,n),a=Hr(e,n),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const o={installation:{sdkVersion:Tt,appId:e.appId}},i={method:"POST",headers:a,body:JSON.stringify(o)},c=await $t(()=>fetch(r,i));if(c.ok){const l=await c.json();return Ot(l)}else throw await Rt("Generate Auth Token",c)}function ca(e,{fid:t}){return`${Dt(e)}/${t}/authTokens:generate`}/**
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
 */async function Se(e,t=!1){let n;const r=await z(e.appConfig,s=>{if(!Bt(s))throw $.create("not-registered");const o=s.authToken;if(!t&&da(o))return s;if(o.requestStatus===1)return n=la(e,t),s;{if(!navigator.onLine)throw $.create("app-offline");const i=fa(s);return n=ua(e,i),i}});return n?await n:r.authToken}async function la(e,t){let n=await Ge(e.appConfig);for(;n.authToken.requestStatus===1;)await kt(100),n=await Ge(e.appConfig);const r=n.authToken;return r.requestStatus===0?Se(e,t):r}function Ge(e){return z(e,t=>{if(!Bt(t))throw $.create("not-registered");const n=t.authToken;return ga(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function ua(e,t){try{const n=await ia(e,t),r=Object.assign(Object.assign({},t),{authToken:n});return await H(e.appConfig,r),n}catch(n){if(At(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await Ft(e.appConfig);else{const r=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await H(e.appConfig,r)}throw n}}function Bt(e){return e!==void 0&&e.registrationStatus===2}function da(e){return e.requestStatus===2&&!ha(e)}function ha(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+xr}function fa(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function ga(e){return e.requestStatus===1&&e.requestTime+yt<Date.now()}/**
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
 */async function pa(e){const t=e,{installationEntry:n,registrationPromise:r}=await Te(t);return r?r.catch(console.error):Se(t).catch(console.error),n.fid}/**
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
 */async function ma(e,t=!1){const n=e;return await Ca(n),(await Se(n,t)).token}async function Ca(e){const{registrationPromise:t}=await Te(e);t&&await t}/**
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
 */function Ia(e){if(!e||!e.options)throw se("App Configuration");if(!e.name)throw se("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw se(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function se(e){return $.create("missing-app-config-values",{valueName:e})}/**
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
 */const xt="installations",_a="installations-internal",ba=e=>{const t=e.getProvider("app").getImmediate(),n=Ia(t),r=G(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:r,_delete:()=>Promise.resolve()}},Ea=e=>{const t=e.getProvider("app").getImmediate(),n=G(t,xt).getImmediate();return{getId:()=>pa(n),getToken:a=>ma(n,a)}};function wa(){b(new R(xt,ba,"PUBLIC")),b(new R(_a,Ea,"PRIVATE"))}wa();_(wt,we);_(wt,we,"esm2017");/**
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
 */const We="analytics",ya="firebase_id",Ta="origin",Sa=60*1e3,Aa="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",Ae="https://www.googletagmanager.com/gtag/js";/**
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
 */const m=new Ie("@firebase/analytics");/**
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
 */const Da={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-intialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},C=new q("analytics","Analytics",Da);/**
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
 */function Oa(e){if(!e.startsWith(Ae)){const t=C.create("invalid-gtag-resource",{gtagURL:e});return m.warn(t.message),""}return e}function Kt(e){return Promise.all(e.map(t=>t.catch(n=>n)))}function Ra(e,t){let n;return window.trustedTypes&&(n=window.trustedTypes.createPolicy(e,t)),n}function La(e,t){const n=Ra("firebase-js-sdk-policy",{createScriptURL:Oa}),r=document.createElement("script"),a=`${Ae}?l=${e}&id=${t}`;r.src=n?n==null?void 0:n.createScriptURL(a):a,r.async=!0,document.head.appendChild(r)}function $a(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function ka(e,t,n,r,a,s){const o=r[a];try{if(o)await t[o];else{const c=(await Kt(n)).find(l=>l.measurementId===a);c&&await t[c.appId]}}catch(i){m.error(i)}e("config",a,s)}async function Ma(e,t,n,r,a){try{let s=[];if(a&&a.send_to){let o=a.send_to;Array.isArray(o)||(o=[o]);const i=await Kt(n);for(const c of o){const l=i.find(h=>h.measurementId===c),u=l&&t[l.appId];if(u)s.push(u);else{s=[];break}}}s.length===0&&(s=Object.values(t)),await Promise.all(s),e("event",r,a||{})}catch(s){m.error(s)}}function Pa(e,t,n,r){async function a(s,...o){try{if(s==="event"){const[i,c]=o;await Ma(e,t,n,i,c)}else if(s==="config"){const[i,c]=o;await ka(e,t,n,r,i,c)}else if(s==="consent"){const[i]=o;e("consent","update",i)}else if(s==="get"){const[i,c,l]=o;e("get",i,c,l)}else if(s==="set"){const[i]=o;e("set",i)}else e(s,...o)}catch(i){m.error(i)}}return a}function Na(e,t,n,r,a){let s=function(...o){window[r].push(arguments)};return window[a]&&typeof window[a]=="function"&&(s=window[a]),window[a]=Pa(s,e,t,n),{gtagCore:s,wrappedGtag:window[a]}}function Fa(e){const t=window.document.getElementsByTagName("script");for(const n of Object.values(t))if(n.src&&n.src.includes(Ae)&&n.src.includes(e))return n;return null}/**
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
 */const va=30,Ba=1e3;class xa{constructor(t={},n=Ba){this.throttleMetadata=t,this.intervalMillis=n}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,n){this.throttleMetadata[t]=n}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const jt=new xa;function Ka(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function ja(e){var t;const{appId:n,apiKey:r}=e,a={method:"GET",headers:Ka(r)},s=Aa.replace("{app-id}",n),o=await fetch(s,a);if(o.status!==200&&o.status!==304){let i="";try{const c=await o.json();!((t=c.error)===null||t===void 0)&&t.message&&(i=c.error.message)}catch{}throw C.create("config-fetch-failed",{httpStatus:o.status,responseMessage:i})}return o.json()}async function Va(e,t=jt,n){const{appId:r,apiKey:a,measurementId:s}=e.options;if(!r)throw C.create("no-app-id");if(!a){if(s)return{measurementId:s,appId:r};throw C.create("no-api-key")}const o=t.getThrottleMetadata(r)||{backoffCount:0,throttleEndTimeMillis:Date.now()},i=new qa;return setTimeout(async()=>{i.abort()},n!==void 0?n:Sa),Vt({appId:r,apiKey:a,measurementId:s},o,i,t)}async function Vt(e,{throttleEndTimeMillis:t,backoffCount:n},r,a=jt){var s;const{appId:o,measurementId:i}=e;try{await Ha(r,t)}catch(c){if(i)return m.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${i} provided in the "measurementId" field in the local Firebase config. [${c==null?void 0:c.message}]`),{appId:o,measurementId:i};throw c}try{const c=await ja(e);return a.deleteThrottleMetadata(o),c}catch(c){const l=c;if(!Ua(l)){if(a.deleteThrottleMetadata(o),i)return m.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${i} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:o,measurementId:i};throw c}const u=Number((s=l==null?void 0:l.customData)===null||s===void 0?void 0:s.httpStatus)===503?Me(n,a.intervalMillis,va):Me(n,a.intervalMillis),h={throttleEndTimeMillis:Date.now()+u,backoffCount:n+1};return a.setThrottleMetadata(o,h),m.debug(`Calling attemptFetch again in ${u} millis`),Vt(e,h,r,a)}}function Ha(e,t){return new Promise((n,r)=>{const a=Math.max(t-Date.now(),0),s=setTimeout(n,a);e.addEventListener(()=>{clearTimeout(s),r(C.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function Ua(e){if(!(e instanceof x)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class qa{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function Ga(e,t,n,r,a){if(a&&a.global){e("event",n,r);return}else{const s=await t,o=Object.assign(Object.assign({},r),{send_to:s});e("event",n,o)}}/**
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
 */async function Wa(){if(ht())try{await ft()}catch(e){return m.warn(C.create("indexeddb-unavailable",{errorInfo:e==null?void 0:e.toString()}).message),!1}else return m.warn(C.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function za(e,t,n,r,a,s,o){var i;const c=Va(e);c.then(g=>{n[g.measurementId]=g.appId,e.options.measurementId&&g.measurementId!==e.options.measurementId&&m.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${g.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(g=>m.error(g)),t.push(c);const l=Wa().then(g=>{if(g)return r.getId()}),[u,h]=await Promise.all([c,l]);Fa(s)||La(s,u.measurementId),a("js",new Date);const f=(i=o==null?void 0:o.config)!==null&&i!==void 0?i:{};return f[Ta]="firebase",f.update=!0,h!=null&&(f[ya]=h),a("config",u.measurementId,f),u.measurementId}/**
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
 */class Ya{constructor(t){this.app=t}_delete(){return delete v[this.app.options.appId],Promise.resolve()}}let v={},ze=[];const Ye={};let oe="dataLayer",Ja="gtag",Je,Ht,Xe=!1;function Xa(){const e=[];if(mn()&&e.push("This is a browser extension environment."),Cn()||e.push("Cookies are not available."),e.length>0){const t=e.map((r,a)=>`(${a+1}) ${r}`).join(" "),n=C.create("invalid-analytics-context",{errorInfo:t});m.warn(n.message)}}function Qa(e,t,n){Xa();const r=e.options.appId;if(!r)throw C.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)m.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw C.create("no-api-key");if(v[r]!=null)throw C.create("already-exists",{id:r});if(!Xe){$a(oe);const{wrappedGtag:s,gtagCore:o}=Na(v,ze,Ye,oe,Ja);Ht=s,Je=o,Xe=!0}return v[r]=za(e,ze,Ye,t,Je,oe,n),new Ya(e)}function Za(e,t,n,r){e=Sn(e),Ga(Ht,v[e.app.options.appId],t,n,r).catch(a=>m.error(a))}const Qe="@firebase/analytics",Ze="0.10.0";function es(){b(new R(We,(t,{options:n})=>{const r=t.getProvider("app").getImmediate(),a=t.getProvider("installations-internal").getImmediate();return Qa(r,a,n)},"PUBLIC")),b(new R("analytics-internal",e,"PRIVATE")),_(Qe,Ze),_(Qe,Ze,"esm2017");function e(t){try{const n=t.getProvider(We).getImmediate();return{logEvent:(r,a,s)=>Za(n,r,a,s)}}catch(n){throw C.create("interop-component-reg-failed",{reason:n})}}}es();function ts(){try{return typeof indexedDB=="object"}catch{return!1}}/**
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
 */const ns="FirebaseError";class K extends Error{constructor(t,n,r){super(n),this.code=t,this.customData=r,this.name=ns,Object.setPrototypeOf(this,K.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,De.prototype.create)}}class De{constructor(t,n,r){this.service=t,this.serviceName=n,this.errors=r}create(t,...n){const r=n[0]||{},a=`${this.service}/${t}`,s=this.errors[t],o=s?rs(s,r):"Error",i=`${this.serviceName}: ${o} (${a}).`;return new K(a,i,r)}}function rs(e,t){return e.replace(as,(n,r)=>{const a=t[r];return a!=null?String(a):`<${r}?>`})}const as=/\{\$([^}]+)}/g;/**
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
 */const ss=1e3,os=2,is=4*60*60*1e3,cs=.5;function ls(e,t=ss,n=os){const r=t*Math.pow(n,e),a=Math.round(cs*r*(Math.random()-.5)*2);return Math.min(is,r+a)}/**
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
 */function us(e){return e&&e._delegate?e._delegate:e}class me{constructor(t,n,r){this.name=t,this.instanceFactory=n,this.type=r,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}const Ut="@firebase/installations",Oe="0.6.5";/**
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
 */const qt=1e4,Gt=`w:${Oe}`,Wt="FIS_v2",ds="https://firebaseinstallations.googleapis.com/v1",hs=60*60*1e3,fs="installations",gs="Installations";/**
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
 */const ps={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},M=new De(fs,gs,ps);function zt(e){return e instanceof K&&e.code.includes("request-failed")}/**
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
 */function Yt({projectId:e}){return`${ds}/projects/${e}/installations`}function Jt(e){return{token:e.token,requestStatus:2,expiresIn:Cs(e.expiresIn),creationTime:Date.now()}}async function Xt(e,t){const r=(await t.json()).error;return M.create("request-failed",{requestName:e,serverCode:r.code,serverMessage:r.message,serverStatus:r.status})}function Qt({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function ms(e,{refreshToken:t}){const n=Qt(e);return n.append("Authorization",Is(t)),n}async function Zt(e){const t=await e();return t.status>=500&&t.status<600?e():t}function Cs(e){return Number(e.replace("s","000"))}function Is(e){return`${Wt} ${e}`}/**
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
 */async function _s({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const r=Yt(e),a=Qt(e),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const o={fid:n,authVersion:Wt,appId:e.appId,sdkVersion:Gt},i={method:"POST",headers:a,body:JSON.stringify(o)},c=await Zt(()=>fetch(r,i));if(c.ok){const l=await c.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:Jt(l.authToken)}}else throw await Xt("Create Installation",c)}/**
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
 */function en(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function bs(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const Es=/^[cdef][\w-]{21}$/,Ce="";function ws(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=ys(e);return Es.test(n)?n:Ce}catch{return Ce}}function ys(e){return bs(e).substr(0,22)}/**
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
 */function Y(e){return`${e.appName}!${e.appId}`}/**
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
 */const tn=new Map;function nn(e,t){const n=Y(e);rn(n,t),Ts(n,t)}function rn(e,t){const n=tn.get(e);if(n)for(const r of n)r(t)}function Ts(e,t){const n=Ss();n&&n.postMessage({key:e,fid:t}),As()}let D=null;function Ss(){return!D&&"BroadcastChannel"in self&&(D=new BroadcastChannel("[Firebase] FID Change"),D.onmessage=e=>{rn(e.data.key,e.data.fid)}),D}function As(){tn.size===0&&D&&(D.close(),D=null)}/**
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
 */const Ds="firebase-installations-database",Os=1,P="firebase-installations-store";let ie=null;function Re(){return ie||(ie=Ct(Ds,Os,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(P)}}})),ie}async function U(e,t){const n=Y(e),a=(await Re()).transaction(P,"readwrite"),s=a.objectStore(P),o=await s.get(n);return await s.put(t,n),await a.done,(!o||o.fid!==t.fid)&&nn(e,t.fid),t}async function an(e){const t=Y(e),r=(await Re()).transaction(P,"readwrite");await r.objectStore(P).delete(t),await r.done}async function J(e,t){const n=Y(e),a=(await Re()).transaction(P,"readwrite"),s=a.objectStore(P),o=await s.get(n),i=t(o);return i===void 0?await s.delete(n):await s.put(i,n),await a.done,i&&(!o||o.fid!==i.fid)&&nn(e,i.fid),i}/**
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
 */async function Le(e){let t;const n=await J(e.appConfig,r=>{const a=Rs(r),s=Ls(e,a);return t=s.registrationPromise,s.installationEntry});return n.fid===Ce?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function Rs(e){const t=e||{fid:ws(),registrationStatus:0};return sn(t)}function Ls(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const a=Promise.reject(M.create("app-offline"));return{installationEntry:t,registrationPromise:a}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},r=$s(e,n);return{installationEntry:n,registrationPromise:r}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:ks(e)}:{installationEntry:t}}async function $s(e,t){try{const n=await _s(e,t);return U(e.appConfig,n)}catch(n){throw zt(n)&&n.customData.serverCode===409?await an(e.appConfig):await U(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function ks(e){let t=await et(e.appConfig);for(;t.registrationStatus===1;)await en(100),t=await et(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:r}=await Le(e);return r||n}return t}function et(e){return J(e,t=>{if(!t)throw M.create("installation-not-found");return sn(t)})}function sn(e){return Ms(e)?{fid:e.fid,registrationStatus:0}:e}function Ms(e){return e.registrationStatus===1&&e.registrationTime+qt<Date.now()}/**
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
 */async function Ps({appConfig:e,heartbeatServiceProvider:t},n){const r=Ns(e,n),a=ms(e,n),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&a.append("x-firebase-client",l)}const o={installation:{sdkVersion:Gt,appId:e.appId}},i={method:"POST",headers:a,body:JSON.stringify(o)},c=await Zt(()=>fetch(r,i));if(c.ok){const l=await c.json();return Jt(l)}else throw await Xt("Generate Auth Token",c)}function Ns(e,{fid:t}){return`${Yt(e)}/${t}/authTokens:generate`}/**
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
 */async function $e(e,t=!1){let n;const r=await J(e.appConfig,s=>{if(!on(s))throw M.create("not-registered");const o=s.authToken;if(!t&&Bs(o))return s;if(o.requestStatus===1)return n=Fs(e,t),s;{if(!navigator.onLine)throw M.create("app-offline");const i=Ks(s);return n=vs(e,i),i}});return n?await n:r.authToken}async function Fs(e,t){let n=await tt(e.appConfig);for(;n.authToken.requestStatus===1;)await en(100),n=await tt(e.appConfig);const r=n.authToken;return r.requestStatus===0?$e(e,t):r}function tt(e){return J(e,t=>{if(!on(t))throw M.create("not-registered");const n=t.authToken;return js(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function vs(e,t){try{const n=await Ps(e,t),r=Object.assign(Object.assign({},t),{authToken:n});return await U(e.appConfig,r),n}catch(n){if(zt(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await an(e.appConfig);else{const r=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await U(e.appConfig,r)}throw n}}function on(e){return e!==void 0&&e.registrationStatus===2}function Bs(e){return e.requestStatus===2&&!xs(e)}function xs(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+hs}function Ks(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function js(e){return e.requestStatus===1&&e.requestTime+qt<Date.now()}/**
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
 */async function Vs(e){const t=e,{installationEntry:n,registrationPromise:r}=await Le(t);return r?r.catch(console.error):$e(t).catch(console.error),n.fid}/**
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
 */async function Hs(e,t=!1){const n=e;return await Us(n),(await $e(n,t)).token}async function Us(e){const{registrationPromise:t}=await Le(e);t&&await t}/**
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
 */function qs(e){if(!e||!e.options)throw ce("App Configuration");if(!e.name)throw ce("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw ce(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function ce(e){return M.create("missing-app-config-values",{valueName:e})}/**
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
 */const cn="installations",Gs="installations-internal",Ws=e=>{const t=e.getProvider("app").getImmediate(),n=qs(t),r=G(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:r,_delete:()=>Promise.resolve()}},zs=e=>{const t=e.getProvider("app").getImmediate(),n=G(t,cn).getImmediate();return{getId:()=>Vs(n),getToken:a=>Hs(n,a)}};function Ys(){b(new me(cn,Ws,"PUBLIC")),b(new me(Gs,zs,"PRIVATE"))}Ys();_(Ut,Oe);_(Ut,Oe,"esm2017");const le="@firebase/remote-config",nt="0.4.5";/**
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
 */const Js="remote-config";/**
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
 */const Xs={"registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser"},p=new De("remoteconfig","Remote Config",Xs);function Qs(e){const t=us(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
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
 */class Zs{constructor(t,n,r,a){this.client=t,this.storage=n,this.storageCache=r,this.logger=a}isCachedDataFresh(t,n){if(!n)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const r=Date.now()-n,a=r<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${r}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${a}.`),a}async fetch(t){const[n,r]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(r&&this.isCachedDataFresh(t.cacheMaxAgeMillis,n))return r;t.eTag=r&&r.eTag;const a=await this.client.fetch(t),s=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return a.status===200&&s.push(this.storage.setLastSuccessfulFetchResponse(a)),await Promise.all(s),a}}/**
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
 */function eo(e=navigator){return e.languages&&e.languages[0]||e.language}/**
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
 */class to{constructor(t,n,r,a,s,o){this.firebaseInstallations=t,this.sdkVersion=n,this.namespace=r,this.projectId=a,this.apiKey=s,this.appId=o}async fetch(t){const[n,r]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),s=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,o={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},i={sdk_version:this.sdkVersion,app_instance_id:n,app_instance_id_token:r,app_id:this.appId,language_code:eo()},c={method:"POST",headers:o,body:JSON.stringify(i)},l=fetch(s,c),u=new Promise((I,w)=>{t.signal.addEventListener(()=>{const ke=new Error("The operation was aborted.");ke.name="AbortError",w(ke)})});let h;try{await Promise.race([l,u]),h=await l}catch(I){let w="fetch-client-network";throw(I==null?void 0:I.name)==="AbortError"&&(w="fetch-timeout"),p.create(w,{originalErrorMessage:I==null?void 0:I.message})}let f=h.status;const g=h.headers.get("ETag")||void 0;let E,F;if(h.status===200){let I;try{I=await h.json()}catch(w){throw p.create("fetch-client-parse",{originalErrorMessage:w==null?void 0:w.message})}E=I.entries,F=I.state}if(F==="INSTANCE_STATE_UNSPECIFIED"?f=500:F==="NO_CHANGE"?f=304:(F==="NO_TEMPLATE"||F==="EMPTY_CONFIG")&&(E={}),f!==304&&f!==200)throw p.create("fetch-status",{httpStatus:f});return{status:f,eTag:g,config:E}}}/**
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
 */function no(e,t){return new Promise((n,r)=>{const a=Math.max(t-Date.now(),0),s=setTimeout(n,a);e.addEventListener(()=>{clearTimeout(s),r(p.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function ro(e){if(!(e instanceof K)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class ao{constructor(t,n){this.client=t,this.storage=n}async fetch(t){const n=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,n)}async attemptFetch(t,{throttleEndTimeMillis:n,backoffCount:r}){await no(t.signal,n);try{const a=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),a}catch(a){if(!ro(a))throw a;const s={throttleEndTimeMillis:Date.now()+ls(r),backoffCount:r+1};return await this.storage.setThrottleMetadata(s),this.attemptFetch(t,s)}}}/**
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
 */const so=60*1e3,oo=12*60*60*1e3;class io{constructor(t,n,r,a,s){this.app=t,this._client=n,this._storageCache=r,this._storage=a,this._logger=s,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:so,minimumFetchIntervalMillis:oo},this.defaultConfig={}}get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}}/**
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
 */function V(e,t){const n=e.target.error||void 0;return p.create(t,{originalErrorMessage:n&&(n==null?void 0:n.message)})}const S="app_namespace_store",co="firebase_remote_config",lo=1;function uo(){return new Promise((e,t)=>{try{const n=indexedDB.open(co,lo);n.onerror=r=>{t(V(r,"storage-open"))},n.onsuccess=r=>{e(r.target.result)},n.onupgradeneeded=r=>{const a=r.target.result;switch(r.oldVersion){case 0:a.createObjectStore(S,{keyPath:"compositeKey"})}}}catch(n){t(p.create("storage-open",{originalErrorMessage:n==null?void 0:n.message}))}})}class ho{constructor(t,n,r,a=uo()){this.appId=t,this.appName=n,this.namespace=r,this.openDbPromise=a}getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}async get(t){const n=await this.openDbPromise;return new Promise((r,a)=>{const o=n.transaction([S],"readonly").objectStore(S),i=this.createCompositeKey(t);try{const c=o.get(i);c.onerror=l=>{a(V(l,"storage-get"))},c.onsuccess=l=>{const u=l.target.result;r(u?u.value:void 0)}}catch(c){a(p.create("storage-get",{originalErrorMessage:c==null?void 0:c.message}))}})}async set(t,n){const r=await this.openDbPromise;return new Promise((a,s)=>{const i=r.transaction([S],"readwrite").objectStore(S),c=this.createCompositeKey(t);try{const l=i.put({compositeKey:c,value:n});l.onerror=u=>{s(V(u,"storage-set"))},l.onsuccess=()=>{a()}}catch(l){s(p.create("storage-set",{originalErrorMessage:l==null?void 0:l.message}))}})}async delete(t){const n=await this.openDbPromise;return new Promise((r,a)=>{const o=n.transaction([S],"readwrite").objectStore(S),i=this.createCompositeKey(t);try{const c=o.delete(i);c.onerror=l=>{a(V(l,"storage-delete"))},c.onsuccess=()=>{r()}}catch(c){a(p.create("storage-delete",{originalErrorMessage:c==null?void 0:c.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}/**
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
 */class fo{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),n=this.storage.getLastSuccessfulFetchTimestampMillis(),r=this.storage.getActiveConfig(),a=await t;a&&(this.lastFetchStatus=a);const s=await n;s&&(this.lastSuccessfulFetchTimestampMillis=s);const o=await r;o&&(this.activeConfig=o)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}}/**
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
 */function go(){b(new me(Js,e,"PUBLIC").setMultipleInstances(!0)),_(le,nt),_(le,nt,"esm2017");function e(t,{instanceIdentifier:n}){const r=t.getProvider("app").getImmediate(),a=t.getProvider("installations-internal").getImmediate();if(typeof window>"u")throw p.create("registration-window");if(!ts())throw p.create("indexed-db-unavailable");const{projectId:s,apiKey:o,appId:i}=r.options;if(!s)throw p.create("registration-project-id");if(!o)throw p.create("registration-api-key");if(!i)throw p.create("registration-app-id");n=n||"firebase";const c=new ho(i,r.name,n),l=new fo(c),u=new Ie(le);u.logLevel=d.ERROR;const h=new to(a,Cr,n,s,o,i),f=new ao(h,c),g=new Zs(f,c,l,u),E=new io(r,g,l,c,u);return Qs(E),E}}go();const ln=N.createContext({});function rt({children:e}){const[t,n]=N.useState();return O.jsx(ln.Provider,{value:{logEvent:t,setLogEvent:n},children:e})}try{rt.displayName="AnalyticsContextProvider",rt.__docgenInfo={description:"",displayName:"AnalyticsContextProvider",props:{}}}catch{}const po=N.createContext({remoteConfig:null,setRemoteConfig:null,remoteConfigData:null,setRemoteConfigData:null});function at({children:e}){const[t,n]=N.useState(null),[r,a]=N.useState(null);return O.jsx(po.Provider,{value:{remoteConfig:t,setRemoteConfig:n,remoteConfigData:r,setRemoteConfigData:a},children:e})}try{at.displayName="RemoteContextProvider",at.__docgenInfo={description:"",displayName:"RemoteContextProvider",props:{}}}catch{}function mo(){return N.useContext(ln)}const st={"help-link":"_help-link_9okj2_2","help-link-text":"_help-link-text_9okj2_10"},Co=()=>{const{logEvent:e}=mo();return O.jsxs("a",{onClick:()=>e==null?void 0:e(lt.CLICKED_HELP_LINK,{from:location.pathname}),className:st["help-link"],href:"https://aide.passculture.app/hc/fr/articles/4411991940369--Acteurs-culturels-Comment-poster-une-offre-%C3%A0-destination-d-un-groupe-scolaire-",rel:"noreferrer",target:"_blank",children:[O.jsx(dn,{src:un,alt:"",width:"42"}),O.jsx("span",{className:st["help-link-text"],children:"Aide"})]})},Io=Co,Do={title:"components/HelpLink",component:Io,decorators:[e=>O.jsx("div",{style:{width:500,height:500},children:O.jsx(e,{})})]},j={};var ot,it,ct;j.parameters={...j.parameters,docs:{...(ot=j.parameters)==null?void 0:ot.docs,source:{originalSource:"{}",...(ct=(it=j.parameters)==null?void 0:it.docs)==null?void 0:ct.source}}};const Oo=["Default"];export{j as Default,Oo as __namedExportsOrder,Do as default};
