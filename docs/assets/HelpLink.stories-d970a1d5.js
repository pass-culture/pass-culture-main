import{j as R}from"./jsx-runtime-ffb262ed.js";import{r as k}from"./index-76fb7be0.js";import"./config-cb91ff0d.js";import{f as At}from"./full-help-fde5c800.js";import{S as Ot}from"./SvgIcon-c0bf369c.js";import"./_commonjsHelpers-de833af9.js";var Ge=(e=>(e.CLICKED_BOOKING="hasClickedBooking",e.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",e.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",e.CLICKED_BREADCRUMBS_PROFILE_AND_HELP="hasClickedProfileAndHelp",e.CLICKED_BREADCRUMBS_STRUCTURES="hasClickedStructures",e.CLICKED_BREADCRUMBS_OFFERER_STATS="hasClickedBreadcrumOffererStats",e.CLICKED_CONSULT_CGU="hasClickedConsultCGU",e.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",e.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",e.CLICKED_CREATE_VENUE="hasClickedCreateVenue",e.CLICKED_ADD_BANK_INFORMATIONS="hasClickedAddBankInformation",e.CLICKED_NO_PRICING_POINT_SELECTED_YET="hasClickedNoPricingPointSelectedYet",e.CLICKED_ADD_VENUE_IN_OFFERER="hasClickedAddVenueInOfferer",e.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",e.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",e.CLICKED_SAVE_VENUE="hasClickedSaveVenue",e.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",e.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",e.CLICKED_DOWNLOAD_BOOKINGS_OTHER_FORMAT="hasClickedDownloadBookingOtherFormat",e.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",e.CLICKED_EDIT_PROFILE="hasClickedEditProfile",e.CLICKED_FAQ="hasClickedFaq",e.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",e.CLICKED_HELP_CENTER="hasClickedHelpCenter",e.CLICKED_HOME="hasClickedHome",e.CLICKED_LOGOUT="hasClickedLogout",e.CLICKED_MODIFY_OFFERER="hasClickedModifyOfferer",e.CLICKED_OFFER="hasClickedOffer",e.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",e.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",e.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",e.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",e.CLICKED_PRO="hasClickedPro",e.CLICKED_REIMBURSEMENT="hasClickedReimbursement",e.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",e.CLICKED_STATS="hasClickedOffererStats",e.CLICKED_TICKET="hasClickedTicket",e.CLICKED_TOGGLE_HIDE_OFFERER_NAME="hasClickedToggleHideOffererName",e.CLICKED_VIEW_OFFERER_STATS="hasClickedViewOffererStats",e.CLICKED_VIEW_ALL_OFFERER_STATS="hasClickedViewAllOffererStats",e.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",e.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",e.CLICKED_HELP_LINK="hasClickedHelpLink",e.CLICKED_RESET_FILTERS="hasClickedResetFilter",e.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",e.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",e.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",e.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",e.FIRST_LOGIN="firstLogin",e.PAGE_VIEW="page_view",e.SIGNUP_FORM_ABORT="signupFormAbort",e.SIGNUP_FORM_SUCCESS="signupFormSuccess",e.TUTO_PAGE_VIEW="tutoPageView",e.DELETE_DRAFT_OFFER="DeleteDraftOffer",e.CLICKED_NO_VENUE="hasClickedNoVenue",e.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",e.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",e.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",e.CLICKED_ADD_IMAGE="hasClickedAddImage",e.CLICKED_DELETE_STOCK="hasClickedDeleteStock",e.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",e))(Ge||{});/**
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
 *//**
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
 */const We=function(e){const t=[];let n=0;for(let a=0;a<e.length;a++){let r=e.charCodeAt(a);r<128?t[n++]=r:r<2048?(t[n++]=r>>6|192,t[n++]=r&63|128):(r&64512)===55296&&a+1<e.length&&(e.charCodeAt(a+1)&64512)===56320?(r=65536+((r&1023)<<10)+(e.charCodeAt(++a)&1023),t[n++]=r>>18|240,t[n++]=r>>12&63|128,t[n++]=r>>6&63|128,t[n++]=r&63|128):(t[n++]=r>>12|224,t[n++]=r>>6&63|128,t[n++]=r&63|128)}return t},Rt=function(e){const t=[];let n=0,a=0;for(;n<e.length;){const r=e[n++];if(r<128)t[a++]=String.fromCharCode(r);else if(r>191&&r<224){const s=e[n++];t[a++]=String.fromCharCode((r&31)<<6|s&63)}else if(r>239&&r<365){const s=e[n++],i=e[n++],c=e[n++],o=((r&7)<<18|(s&63)<<12|(i&63)<<6|c&63)-65536;t[a++]=String.fromCharCode(55296+(o>>10)),t[a++]=String.fromCharCode(56320+(o&1023))}else{const s=e[n++],i=e[n++];t[a++]=String.fromCharCode((r&15)<<12|(s&63)<<6|i&63)}}return t.join("")},Lt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const n=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,a=[];for(let r=0;r<e.length;r+=3){const s=e[r],i=r+1<e.length,c=i?e[r+1]:0,o=r+2<e.length,l=o?e[r+2]:0,d=s>>2,h=(s&3)<<4|c>>4;let f=(c&15)<<2|l>>6,g=l&63;o||(g=64,i||(f=64)),a.push(n[d],n[h],n[f],n[g])}return a.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(We(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):Rt(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const n=t?this.charToByteMapWebSafe_:this.charToByteMap_,a=[];for(let r=0;r<e.length;){const s=n[e.charAt(r++)],c=r<e.length?n[e.charAt(r)]:0;++r;const l=r<e.length?n[e.charAt(r)]:64;++r;const h=r<e.length?n[e.charAt(r)]:64;if(++r,s==null||c==null||l==null||h==null)throw new Mt;const f=s<<2|c>>4;if(a.push(f),l!==64){const g=c<<4&240|l>>2;if(a.push(g),h!==64){const E=l<<6&192|h;a.push(E)}}}return a},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class Mt extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const Ft=function(e){const t=We(e);return Lt.encodeByteArray(t,!0)},qe=function(e){return Ft(e).replace(/\./g,"")};function kt(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function oe(){try{return typeof indexedDB=="object"}catch{return!1}}function ze(){return new Promise((e,t)=>{try{let n=!0;const a="validate-browser-context-for-indexeddb-analytics-module",r=self.indexedDB.open(a);r.onsuccess=()=>{r.result.close(),n||self.indexedDB.deleteDatabase(a),e(!0)},r.onupgradeneeded=()=>{n=!1},r.onerror=()=>{var s;t(((s=r.error)===null||s===void 0?void 0:s.message)||"")}}catch(n){t(n)}})}function Pt(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const Nt="FirebaseError";class D extends Error{constructor(t,n,a){super(n),this.code=t,this.customData=a,this.name=Nt,Object.setPrototypeOf(this,D.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,B.prototype.create)}}class B{constructor(t,n,a){this.service=t,this.serviceName=n,this.errors=a}create(t,...n){const a=n[0]||{},r=`${this.service}/${t}`,s=this.errors[t],i=s?vt(s,a):"Error",c=`${this.serviceName}: ${i} (${r}).`;return new D(r,c,a)}}function vt(e,t){return e.replace(Bt,(n,a)=>{const r=t[a];return r!=null?String(r):`<${a}?>`})}const Bt=/\{\$([^}]+)}/g;/**
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
 */const $t=1e3,xt=2,Kt=4*60*60*1e3,jt=.5;function ee(e,t=$t,n=xt){const a=t*Math.pow(n,e),r=Math.round(jt*a*(Math.random()-.5)*2);return Math.min(Kt,a+r)}/**
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
 */function Ye(e){return e&&e._delegate?e._delegate:e}class S{constructor(t,n,a){this.name=t,this.instanceFactory=n,this.type=a,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}/**
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
 */var u;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(u||(u={}));const Ht={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},Vt=u.INFO,Ut={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},Gt=(e,t,...n)=>{if(t<e.logLevel)return;const a=new Date().toISOString(),r=Ut[t];if(r)console[r](`[${a}]  ${e.name}:`,...n);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class ce{constructor(t){this.name=t,this._logLevel=Vt,this._logHandler=Gt,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in u))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?Ht[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...t),this._logHandler(this,u.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...t),this._logHandler(this,u.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,u.INFO,...t),this._logHandler(this,u.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,u.WARN,...t),this._logHandler(this,u.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...t),this._logHandler(this,u.ERROR,...t)}}const Wt=(e,t)=>t.some(n=>e instanceof n);let _e,Ie;function qt(){return _e||(_e=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function zt(){return Ie||(Ie=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const Je=new WeakMap,te=new WeakMap,Xe=new WeakMap,V=new WeakMap,le=new WeakMap;function Yt(e){const t=new Promise((n,a)=>{const r=()=>{e.removeEventListener("success",s),e.removeEventListener("error",i)},s=()=>{n(w(e.result)),r()},i=()=>{a(e.error),r()};e.addEventListener("success",s),e.addEventListener("error",i)});return t.then(n=>{n instanceof IDBCursor&&Je.set(n,e)}).catch(()=>{}),le.set(t,e),t}function Jt(e){if(te.has(e))return;const t=new Promise((n,a)=>{const r=()=>{e.removeEventListener("complete",s),e.removeEventListener("error",i),e.removeEventListener("abort",i)},s=()=>{n(),r()},i=()=>{a(e.error||new DOMException("AbortError","AbortError")),r()};e.addEventListener("complete",s),e.addEventListener("error",i),e.addEventListener("abort",i)});te.set(e,t)}let ne={get(e,t,n){if(e instanceof IDBTransaction){if(t==="done")return te.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Xe.get(e);if(t==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return w(e[t])},set(e,t,n){return e[t]=n,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function Xt(e){ne=e(ne)}function Qt(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...n){const a=e.call(U(this),t,...n);return Xe.set(a,t.sort?t.sort():[t]),w(a)}:zt().includes(e)?function(...t){return e.apply(U(this),t),w(Je.get(this))}:function(...t){return w(e.apply(U(this),t))}}function Zt(e){return typeof e=="function"?Qt(e):(e instanceof IDBTransaction&&Jt(e),Wt(e,qt())?new Proxy(e,ne):e)}function w(e){if(e instanceof IDBRequest)return Yt(e);if(V.has(e))return V.get(e);const t=Zt(e);return t!==e&&(V.set(e,t),le.set(t,e)),t}const U=e=>le.get(e);function en(e,t,{blocked:n,upgrade:a,blocking:r,terminated:s}={}){const i=indexedDB.open(e,t),c=w(i);return a&&i.addEventListener("upgradeneeded",o=>{a(w(i.result),o.oldVersion,o.newVersion,w(i.transaction),o)}),n&&i.addEventListener("blocked",o=>n(o.oldVersion,o.newVersion,o)),c.then(o=>{s&&o.addEventListener("close",()=>s()),r&&o.addEventListener("versionchange",l=>r(l.oldVersion,l.newVersion,l))}).catch(()=>{}),c}const tn=["get","getKey","getAll","getAllKeys","count"],nn=["put","add","delete","clear"],G=new Map;function Ee(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(G.get(t))return G.get(t);const n=t.replace(/FromIndex$/,""),a=t!==n,r=nn.includes(n);if(!(n in(a?IDBIndex:IDBObjectStore).prototype)||!(r||tn.includes(n)))return;const s=async function(i,...c){const o=this.transaction(i,r?"readwrite":"readonly");let l=o.store;return a&&(l=l.index(c.shift())),(await Promise.all([l[n](...c),r&&o.done]))[0]};return G.set(t,s),s}Xt(e=>({...e,get:(t,n,a)=>Ee(t,n)||e.get(t,n,a),has:(t,n)=>!!Ee(t,n)||e.has(t,n)}));/**
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
 */class rn{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(n=>{if(an(n)){const a=n.getImmediate();return`${a.library}/${a.version}`}else return null}).filter(n=>n).join(" ")}}function an(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const re="@firebase/app",be="0.9.23";/**
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
 */const L=new ce("@firebase/app"),sn="@firebase/app-compat",on="@firebase/analytics-compat",cn="@firebase/analytics",ln="@firebase/app-check-compat",un="@firebase/app-check",dn="@firebase/auth",hn="@firebase/auth-compat",fn="@firebase/database",gn="@firebase/database-compat",pn="@firebase/functions",mn="@firebase/functions-compat",Cn="@firebase/installations",_n="@firebase/installations-compat",In="@firebase/messaging",En="@firebase/messaging-compat",bn="@firebase/performance",wn="@firebase/performance-compat",yn="@firebase/remote-config",Sn="@firebase/remote-config-compat",Tn="@firebase/storage",Dn="@firebase/storage-compat",An="@firebase/firestore",On="@firebase/firestore-compat",Rn="firebase",Ln="10.6.0",Mn={[re]:"fire-core",[sn]:"fire-core-compat",[cn]:"fire-analytics",[on]:"fire-analytics-compat",[un]:"fire-app-check",[ln]:"fire-app-check-compat",[dn]:"fire-auth",[hn]:"fire-auth-compat",[fn]:"fire-rtdb",[gn]:"fire-rtdb-compat",[pn]:"fire-fn",[mn]:"fire-fn-compat",[Cn]:"fire-iid",[_n]:"fire-iid-compat",[In]:"fire-fcm",[En]:"fire-fcm-compat",[bn]:"fire-perf",[wn]:"fire-perf-compat",[yn]:"fire-rc",[Sn]:"fire-rc-compat",[Tn]:"fire-gcs",[Dn]:"fire-gcs-compat",[An]:"fire-fst",[On]:"fire-fst-compat","fire-js":"fire-js",[Rn]:"fire-js-all"};/**
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
 */const Fn=new Map,we=new Map;function kn(e,t){try{e.container.addComponent(t)}catch(n){L.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,n)}}function T(e){const t=e.name;if(we.has(t))return L.debug(`There were multiple attempts to register component ${t}.`),!1;we.set(t,e);for(const n of Fn.values())kn(n,e);return!0}function Qe(e,t){const n=e.container.getProvider("heartbeat").getImmediate({optional:!0});return n&&n.triggerHeartbeat(),e.container.getProvider(t)}/**
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
 */const Pn={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}."},ue=new B("app","Firebase",Pn);/**
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
 */const Nn=Ln;function I(e,t,n){var a;let r=(a=Mn[e])!==null&&a!==void 0?a:e;n&&(r+=`-${n}`);const s=r.match(/\s|\//),i=t.match(/\s|\//);if(s||i){const c=[`Unable to register library "${r}" with version "${t}":`];s&&c.push(`library name "${r}" contains illegal characters (whitespace or "/")`),s&&i&&c.push("and"),i&&c.push(`version name "${t}" contains illegal characters (whitespace or "/")`),L.warn(c.join(" "));return}T(new S(`${r}-version`,()=>({library:r,version:t}),"VERSION"))}/**
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
 */const vn="firebase-heartbeat-database",Bn=1,v="firebase-heartbeat-store";let W=null;function Ze(){return W||(W=en(vn,Bn,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(v)}}}).catch(e=>{throw ue.create("idb-open",{originalErrorMessage:e.message})})),W}async function $n(e){try{return await(await Ze()).transaction(v).objectStore(v).get(et(e))}catch(t){if(t instanceof D)L.warn(t.message);else{const n=ue.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});L.warn(n.message)}}}async function ye(e,t){try{const a=(await Ze()).transaction(v,"readwrite");await a.objectStore(v).put(t,et(e)),await a.done}catch(n){if(n instanceof D)L.warn(n.message);else{const a=ue.create("idb-set",{originalErrorMessage:n==null?void 0:n.message});L.warn(a.message)}}}function et(e){return`${e.name}!${e.options.appId}`}/**
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
 */const xn=1024,Kn=30*24*60*60*1e3;class jn{constructor(t){this.container=t,this._heartbeatsCache=null;const n=this.container.getProvider("app").getImmediate();this._storage=new Vn(n),this._heartbeatsCachePromise=this._storage.read().then(a=>(this._heartbeatsCache=a,a))}async triggerHeartbeat(){var t;const a=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),r=Se();if(((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise),!(this._heartbeatsCache.lastSentHeartbeatDate===r||this._heartbeatsCache.heartbeats.some(s=>s.date===r)))return this._heartbeatsCache.heartbeats.push({date:r,agent:a}),this._heartbeatsCache.heartbeats=this._heartbeatsCache.heartbeats.filter(s=>{const i=new Date(s.date).valueOf();return Date.now()-i<=Kn}),this._storage.overwrite(this._heartbeatsCache)}async getHeartbeatsHeader(){var t;if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const n=Se(),{heartbeatsToSend:a,unsentEntries:r}=Hn(this._heartbeatsCache.heartbeats),s=qe(JSON.stringify({version:2,heartbeats:a}));return this._heartbeatsCache.lastSentHeartbeatDate=n,r.length>0?(this._heartbeatsCache.heartbeats=r,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}}function Se(){return new Date().toISOString().substring(0,10)}function Hn(e,t=xn){const n=[];let a=e.slice();for(const r of e){const s=n.find(i=>i.agent===r.agent);if(s){if(s.dates.push(r.date),Te(n)>t){s.dates.pop();break}}else if(n.push({agent:r.agent,dates:[r.date]}),Te(n)>t){n.pop();break}a=a.slice(1)}return{heartbeatsToSend:n,unsentEntries:a}}class Vn{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return oe()?ze().then(()=>!0).catch(()=>!1):!1}async read(){return await this._canUseIndexedDBPromise?await $n(this.app)||{heartbeats:[]}:{heartbeats:[]}}async overwrite(t){var n;if(await this._canUseIndexedDBPromise){const r=await this.read();return ye(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:r.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){var n;if(await this._canUseIndexedDBPromise){const r=await this.read();return ye(this.app,{lastSentHeartbeatDate:(n=t.lastSentHeartbeatDate)!==null&&n!==void 0?n:r.lastSentHeartbeatDate,heartbeats:[...r.heartbeats,...t.heartbeats]})}else return}}function Te(e){return qe(JSON.stringify({version:2,heartbeats:e})).length}/**
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
 */function Un(e){T(new S("platform-logger",t=>new rn(t),"PRIVATE")),T(new S("heartbeat",t=>new jn(t),"PRIVATE")),I(re,be,e),I(re,be,"esm2017"),I("fire-js","")}Un("");const Gn=(e,t)=>t.some(n=>e instanceof n);let De,Ae;function Wn(){return De||(De=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function qn(){return Ae||(Ae=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const tt=new WeakMap,ae=new WeakMap,nt=new WeakMap,q=new WeakMap,de=new WeakMap;function zn(e){const t=new Promise((n,a)=>{const r=()=>{e.removeEventListener("success",s),e.removeEventListener("error",i)},s=()=>{n(y(e.result)),r()},i=()=>{a(e.error),r()};e.addEventListener("success",s),e.addEventListener("error",i)});return t.then(n=>{n instanceof IDBCursor&&tt.set(n,e)}).catch(()=>{}),de.set(t,e),t}function Yn(e){if(ae.has(e))return;const t=new Promise((n,a)=>{const r=()=>{e.removeEventListener("complete",s),e.removeEventListener("error",i),e.removeEventListener("abort",i)},s=()=>{n(),r()},i=()=>{a(e.error||new DOMException("AbortError","AbortError")),r()};e.addEventListener("complete",s),e.addEventListener("error",i),e.addEventListener("abort",i)});ae.set(e,t)}let se={get(e,t,n){if(e instanceof IDBTransaction){if(t==="done")return ae.get(e);if(t==="objectStoreNames")return e.objectStoreNames||nt.get(e);if(t==="store")return n.objectStoreNames[1]?void 0:n.objectStore(n.objectStoreNames[0])}return y(e[t])},set(e,t,n){return e[t]=n,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function Jn(e){se=e(se)}function Xn(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...n){const a=e.call(z(this),t,...n);return nt.set(a,t.sort?t.sort():[t]),y(a)}:qn().includes(e)?function(...t){return e.apply(z(this),t),y(tt.get(this))}:function(...t){return y(e.apply(z(this),t))}}function Qn(e){return typeof e=="function"?Xn(e):(e instanceof IDBTransaction&&Yn(e),Gn(e,Wn())?new Proxy(e,se):e)}function y(e){if(e instanceof IDBRequest)return zn(e);if(q.has(e))return q.get(e);const t=Qn(e);return t!==e&&(q.set(e,t),de.set(t,e)),t}const z=e=>de.get(e);function Zn(e,t,{blocked:n,upgrade:a,blocking:r,terminated:s}={}){const i=indexedDB.open(e,t),c=y(i);return a&&i.addEventListener("upgradeneeded",o=>{a(y(i.result),o.oldVersion,o.newVersion,y(i.transaction))}),n&&i.addEventListener("blocked",()=>n()),c.then(o=>{s&&o.addEventListener("close",()=>s()),r&&o.addEventListener("versionchange",()=>r())}).catch(()=>{}),c}const er=["get","getKey","getAll","getAllKeys","count"],tr=["put","add","delete","clear"],Y=new Map;function Oe(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(Y.get(t))return Y.get(t);const n=t.replace(/FromIndex$/,""),a=t!==n,r=tr.includes(n);if(!(n in(a?IDBIndex:IDBObjectStore).prototype)||!(r||er.includes(n)))return;const s=async function(i,...c){const o=this.transaction(i,r?"readwrite":"readonly");let l=o.store;return a&&(l=l.index(c.shift())),(await Promise.all([l[n](...c),r&&o.done]))[0]};return Y.set(t,s),s}Jn(e=>({...e,get:(t,n,a)=>Oe(t,n)||e.get(t,n,a),has:(t,n)=>!!Oe(t,n)||e.has(t,n)}));const rt="@firebase/installations",he="0.6.4";/**
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
 */const at=1e4,st=`w:${he}`,it="FIS_v2",nr="https://firebaseinstallations.googleapis.com/v1",rr=60*60*1e3,ar="installations",sr="Installations";/**
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
 */const ir={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},M=new B(ar,sr,ir);function ot(e){return e instanceof D&&e.code.includes("request-failed")}/**
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
 */function ct({projectId:e}){return`${nr}/projects/${e}/installations`}function lt(e){return{token:e.token,requestStatus:2,expiresIn:cr(e.expiresIn),creationTime:Date.now()}}async function ut(e,t){const a=(await t.json()).error;return M.create("request-failed",{requestName:e,serverCode:a.code,serverMessage:a.message,serverStatus:a.status})}function dt({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function or(e,{refreshToken:t}){const n=dt(e);return n.append("Authorization",lr(t)),n}async function ht(e){const t=await e();return t.status>=500&&t.status<600?e():t}function cr(e){return Number(e.replace("s","000"))}function lr(e){return`${it} ${e}`}/**
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
 */async function ur({appConfig:e,heartbeatServiceProvider:t},{fid:n}){const a=ct(e),r=dt(e),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&r.append("x-firebase-client",l)}const i={fid:n,authVersion:it,appId:e.appId,sdkVersion:st},c={method:"POST",headers:r,body:JSON.stringify(i)},o=await ht(()=>fetch(a,c));if(o.ok){const l=await o.json();return{fid:l.fid||n,registrationStatus:2,refreshToken:l.refreshToken,authToken:lt(l.authToken)}}else throw await ut("Create Installation",o)}/**
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
 */function ft(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function dr(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const hr=/^[cdef][\w-]{21}$/,ie="";function fr(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const n=gr(e);return hr.test(n)?n:ie}catch{return ie}}function gr(e){return dr(e).substr(0,22)}/**
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
 */function j(e){return`${e.appName}!${e.appId}`}/**
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
 */const gt=new Map;function pt(e,t){const n=j(e);mt(n,t),pr(n,t)}function mt(e,t){const n=gt.get(e);if(n)for(const a of n)a(t)}function pr(e,t){const n=mr();n&&n.postMessage({key:e,fid:t}),Cr()}let O=null;function mr(){return!O&&"BroadcastChannel"in self&&(O=new BroadcastChannel("[Firebase] FID Change"),O.onmessage=e=>{mt(e.data.key,e.data.fid)}),O}function Cr(){gt.size===0&&O&&(O.close(),O=null)}/**
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
 */const _r="firebase-installations-database",Ir=1,F="firebase-installations-store";let J=null;function fe(){return J||(J=Zn(_r,Ir,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(F)}}})),J}async function K(e,t){const n=j(e),r=(await fe()).transaction(F,"readwrite"),s=r.objectStore(F),i=await s.get(n);return await s.put(t,n),await r.done,(!i||i.fid!==t.fid)&&pt(e,t.fid),t}async function Ct(e){const t=j(e),a=(await fe()).transaction(F,"readwrite");await a.objectStore(F).delete(t),await a.done}async function H(e,t){const n=j(e),r=(await fe()).transaction(F,"readwrite"),s=r.objectStore(F),i=await s.get(n),c=t(i);return c===void 0?await s.delete(n):await s.put(c,n),await r.done,c&&(!i||i.fid!==c.fid)&&pt(e,c.fid),c}/**
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
 */async function ge(e){let t;const n=await H(e.appConfig,a=>{const r=Er(a),s=br(e,r);return t=s.registrationPromise,s.installationEntry});return n.fid===ie?{installationEntry:await t}:{installationEntry:n,registrationPromise:t}}function Er(e){const t=e||{fid:fr(),registrationStatus:0};return _t(t)}function br(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const r=Promise.reject(M.create("app-offline"));return{installationEntry:t,registrationPromise:r}}const n={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},a=wr(e,n);return{installationEntry:n,registrationPromise:a}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:yr(e)}:{installationEntry:t}}async function wr(e,t){try{const n=await ur(e,t);return K(e.appConfig,n)}catch(n){throw ot(n)&&n.customData.serverCode===409?await Ct(e.appConfig):await K(e.appConfig,{fid:t.fid,registrationStatus:0}),n}}async function yr(e){let t=await Re(e.appConfig);for(;t.registrationStatus===1;)await ft(100),t=await Re(e.appConfig);if(t.registrationStatus===0){const{installationEntry:n,registrationPromise:a}=await ge(e);return a||n}return t}function Re(e){return H(e,t=>{if(!t)throw M.create("installation-not-found");return _t(t)})}function _t(e){return Sr(e)?{fid:e.fid,registrationStatus:0}:e}function Sr(e){return e.registrationStatus===1&&e.registrationTime+at<Date.now()}/**
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
 */async function Tr({appConfig:e,heartbeatServiceProvider:t},n){const a=Dr(e,n),r=or(e,n),s=t.getImmediate({optional:!0});if(s){const l=await s.getHeartbeatsHeader();l&&r.append("x-firebase-client",l)}const i={installation:{sdkVersion:st,appId:e.appId}},c={method:"POST",headers:r,body:JSON.stringify(i)},o=await ht(()=>fetch(a,c));if(o.ok){const l=await o.json();return lt(l)}else throw await ut("Generate Auth Token",o)}function Dr(e,{fid:t}){return`${ct(e)}/${t}/authTokens:generate`}/**
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
 */async function pe(e,t=!1){let n;const a=await H(e.appConfig,s=>{if(!It(s))throw M.create("not-registered");const i=s.authToken;if(!t&&Rr(i))return s;if(i.requestStatus===1)return n=Ar(e,t),s;{if(!navigator.onLine)throw M.create("app-offline");const c=Mr(s);return n=Or(e,c),c}});return n?await n:a.authToken}async function Ar(e,t){let n=await Le(e.appConfig);for(;n.authToken.requestStatus===1;)await ft(100),n=await Le(e.appConfig);const a=n.authToken;return a.requestStatus===0?pe(e,t):a}function Le(e){return H(e,t=>{if(!It(t))throw M.create("not-registered");const n=t.authToken;return Fr(n)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function Or(e,t){try{const n=await Tr(e,t),a=Object.assign(Object.assign({},t),{authToken:n});return await K(e.appConfig,a),n}catch(n){if(ot(n)&&(n.customData.serverCode===401||n.customData.serverCode===404))await Ct(e.appConfig);else{const a=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await K(e.appConfig,a)}throw n}}function It(e){return e!==void 0&&e.registrationStatus===2}function Rr(e){return e.requestStatus===2&&!Lr(e)}function Lr(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+rr}function Mr(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function Fr(e){return e.requestStatus===1&&e.requestTime+at<Date.now()}/**
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
 */async function kr(e){const t=e,{installationEntry:n,registrationPromise:a}=await ge(t);return a?a.catch(console.error):pe(t).catch(console.error),n.fid}/**
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
 */async function Pr(e,t=!1){const n=e;return await Nr(n),(await pe(n,t)).token}async function Nr(e){const{registrationPromise:t}=await ge(e);t&&await t}/**
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
 */function vr(e){if(!e||!e.options)throw X("App Configuration");if(!e.name)throw X("App Name");const t=["projectId","apiKey","appId"];for(const n of t)if(!e.options[n])throw X(n);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function X(e){return M.create("missing-app-config-values",{valueName:e})}/**
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
 */const Et="installations",Br="installations-internal",$r=e=>{const t=e.getProvider("app").getImmediate(),n=vr(t),a=Qe(t,"heartbeat");return{app:t,appConfig:n,heartbeatServiceProvider:a,_delete:()=>Promise.resolve()}},xr=e=>{const t=e.getProvider("app").getImmediate(),n=Qe(t,Et).getImmediate();return{getId:()=>kr(n),getToken:r=>Pr(n,r)}};function Kr(){T(new S(Et,$r,"PUBLIC")),T(new S(Br,xr,"PRIVATE"))}Kr();I(rt,he);I(rt,he,"esm2017");/**
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
 */const Me="analytics",jr="firebase_id",Hr="origin",Vr=60*1e3,Ur="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",me="https://www.googletagmanager.com/gtag/js";/**
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
 */const m=new ce("@firebase/analytics");/**
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
 */const Gr={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-intialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},C=new B("analytics","Analytics",Gr);/**
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
 */function Wr(e){if(!e.startsWith(me)){const t=C.create("invalid-gtag-resource",{gtagURL:e});return m.warn(t.message),""}return e}function bt(e){return Promise.all(e.map(t=>t.catch(n=>n)))}function qr(e,t){let n;return window.trustedTypes&&(n=window.trustedTypes.createPolicy(e,t)),n}function zr(e,t){const n=qr("firebase-js-sdk-policy",{createScriptURL:Wr}),a=document.createElement("script"),r=`${me}?l=${e}&id=${t}`;a.src=n?n==null?void 0:n.createScriptURL(r):r,a.async=!0,document.head.appendChild(a)}function Yr(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function Jr(e,t,n,a,r,s){const i=a[r];try{if(i)await t[i];else{const o=(await bt(n)).find(l=>l.measurementId===r);o&&await t[o.appId]}}catch(c){m.error(c)}e("config",r,s)}async function Xr(e,t,n,a,r){try{let s=[];if(r&&r.send_to){let i=r.send_to;Array.isArray(i)||(i=[i]);const c=await bt(n);for(const o of i){const l=c.find(h=>h.measurementId===o),d=l&&t[l.appId];if(d)s.push(d);else{s=[];break}}}s.length===0&&(s=Object.values(t)),await Promise.all(s),e("event",a,r||{})}catch(s){m.error(s)}}function Qr(e,t,n,a){async function r(s,...i){try{if(s==="event"){const[c,o]=i;await Xr(e,t,n,c,o)}else if(s==="config"){const[c,o]=i;await Jr(e,t,n,a,c,o)}else if(s==="consent"){const[c]=i;e("consent","update",c)}else if(s==="get"){const[c,o,l]=i;e("get",c,o,l)}else if(s==="set"){const[c]=i;e("set",c)}else e(s,...i)}catch(c){m.error(c)}}return r}function Zr(e,t,n,a,r){let s=function(...i){window[a].push(arguments)};return window[r]&&typeof window[r]=="function"&&(s=window[r]),window[r]=Qr(s,e,t,n),{gtagCore:s,wrappedGtag:window[r]}}function ea(e){const t=window.document.getElementsByTagName("script");for(const n of Object.values(t))if(n.src&&n.src.includes(me)&&n.src.includes(e))return n;return null}/**
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
 */const ta=30,na=1e3;class ra{constructor(t={},n=na){this.throttleMetadata=t,this.intervalMillis=n}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,n){this.throttleMetadata[t]=n}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const wt=new ra;function aa(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function sa(e){var t;const{appId:n,apiKey:a}=e,r={method:"GET",headers:aa(a)},s=Ur.replace("{app-id}",n),i=await fetch(s,r);if(i.status!==200&&i.status!==304){let c="";try{const o=await i.json();!((t=o.error)===null||t===void 0)&&t.message&&(c=o.error.message)}catch{}throw C.create("config-fetch-failed",{httpStatus:i.status,responseMessage:c})}return i.json()}async function ia(e,t=wt,n){const{appId:a,apiKey:r,measurementId:s}=e.options;if(!a)throw C.create("no-app-id");if(!r){if(s)return{measurementId:s,appId:a};throw C.create("no-api-key")}const i=t.getThrottleMetadata(a)||{backoffCount:0,throttleEndTimeMillis:Date.now()},c=new la;return setTimeout(async()=>{c.abort()},n!==void 0?n:Vr),yt({appId:a,apiKey:r,measurementId:s},i,c,t)}async function yt(e,{throttleEndTimeMillis:t,backoffCount:n},a,r=wt){var s;const{appId:i,measurementId:c}=e;try{await oa(a,t)}catch(o){if(c)return m.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${c} provided in the "measurementId" field in the local Firebase config. [${o==null?void 0:o.message}]`),{appId:i,measurementId:c};throw o}try{const o=await sa(e);return r.deleteThrottleMetadata(i),o}catch(o){const l=o;if(!ca(l)){if(r.deleteThrottleMetadata(i),c)return m.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${c} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:c};throw o}const d=Number((s=l==null?void 0:l.customData)===null||s===void 0?void 0:s.httpStatus)===503?ee(n,r.intervalMillis,ta):ee(n,r.intervalMillis),h={throttleEndTimeMillis:Date.now()+d,backoffCount:n+1};return r.setThrottleMetadata(i,h),m.debug(`Calling attemptFetch again in ${d} millis`),yt(e,h,a,r)}}function oa(e,t){return new Promise((n,a)=>{const r=Math.max(t-Date.now(),0),s=setTimeout(n,r);e.addEventListener(()=>{clearTimeout(s),a(C.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function ca(e){if(!(e instanceof D)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class la{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function ua(e,t,n,a,r){if(r&&r.global){e("event",n,a);return}else{const s=await t,i=Object.assign(Object.assign({},a),{send_to:s});e("event",n,i)}}/**
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
 */async function da(){if(oe())try{await ze()}catch(e){return m.warn(C.create("indexeddb-unavailable",{errorInfo:e==null?void 0:e.toString()}).message),!1}else return m.warn(C.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function ha(e,t,n,a,r,s,i){var c;const o=ia(e);o.then(g=>{n[g.measurementId]=g.appId,e.options.measurementId&&g.measurementId!==e.options.measurementId&&m.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${g.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(g=>m.error(g)),t.push(o);const l=da().then(g=>{if(g)return a.getId()}),[d,h]=await Promise.all([o,l]);ea(s)||zr(s,d.measurementId),r("js",new Date);const f=(c=i==null?void 0:i.config)!==null&&c!==void 0?c:{};return f[Hr]="firebase",f.update=!0,h!=null&&(f[jr]=h),r("config",d.measurementId,f),d.measurementId}/**
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
 */class fa{constructor(t){this.app=t}_delete(){return delete N[this.app.options.appId],Promise.resolve()}}let N={},Fe=[];const ke={};let Q="dataLayer",ga="gtag",Pe,St,Ne=!1;function pa(){const e=[];if(kt()&&e.push("This is a browser extension environment."),Pt()||e.push("Cookies are not available."),e.length>0){const t=e.map((a,r)=>`(${r+1}) ${a}`).join(" "),n=C.create("invalid-analytics-context",{errorInfo:t});m.warn(n.message)}}function ma(e,t,n){pa();const a=e.options.appId;if(!a)throw C.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)m.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw C.create("no-api-key");if(N[a]!=null)throw C.create("already-exists",{id:a});if(!Ne){Yr(Q);const{wrappedGtag:s,gtagCore:i}=Zr(N,Fe,ke,Q,ga);St=s,Pe=i,Ne=!0}return N[a]=ha(e,Fe,ke,t,Pe,Q,n),new fa(e)}function Ca(e,t,n,a){e=Ye(e),ua(St,N[e.app.options.appId],t,n,a).catch(r=>m.error(r))}const ve="@firebase/analytics",Be="0.10.0";function _a(){T(new S(Me,(t,{options:n})=>{const a=t.getProvider("app").getImmediate(),r=t.getProvider("installations-internal").getImmediate();return ma(a,r,n)},"PUBLIC")),T(new S("analytics-internal",e,"PRIVATE")),I(ve,Be),I(ve,Be,"esm2017");function e(t){try{const n=t.getProvider(Me).getImmediate();return{logEvent:(a,r,s)=>Ca(n,a,r,s)}}catch(n){throw C.create("interop-component-reg-failed",{reason:n})}}}_a();const Z="@firebase/remote-config",$e="0.4.4";/**
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
 */const Ia="remote-config";/**
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
 */const Ea={"registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser"},p=new B("remoteconfig","Remote Config",Ea);function ba(e){const t=Ye(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
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
 */class wa{constructor(t,n,a,r){this.client=t,this.storage=n,this.storageCache=a,this.logger=r}isCachedDataFresh(t,n){if(!n)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const a=Date.now()-n,r=a<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${a}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${r}.`),r}async fetch(t){const[n,a]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(a&&this.isCachedDataFresh(t.cacheMaxAgeMillis,n))return a;t.eTag=a&&a.eTag;const r=await this.client.fetch(t),s=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return r.status===200&&s.push(this.storage.setLastSuccessfulFetchResponse(r)),await Promise.all(s),r}}/**
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
 */function ya(e=navigator){return e.languages&&e.languages[0]||e.language}/**
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
 */class Sa{constructor(t,n,a,r,s,i){this.firebaseInstallations=t,this.sdkVersion=n,this.namespace=a,this.projectId=r,this.apiKey=s,this.appId=i}async fetch(t){const[n,a]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),s=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},c={sdk_version:this.sdkVersion,app_instance_id:n,app_instance_id_token:a,app_id:this.appId,language_code:ya()},o={method:"POST",headers:i,body:JSON.stringify(c)},l=fetch(s,o),d=new Promise((_,b)=>{t.signal.addEventListener(()=>{const Ce=new Error("The operation was aborted.");Ce.name="AbortError",b(Ce)})});let h;try{await Promise.race([l,d]),h=await l}catch(_){let b="fetch-client-network";throw(_==null?void 0:_.name)==="AbortError"&&(b="fetch-timeout"),p.create(b,{originalErrorMessage:_==null?void 0:_.message})}let f=h.status;const g=h.headers.get("ETag")||void 0;let E,P;if(h.status===200){let _;try{_=await h.json()}catch(b){throw p.create("fetch-client-parse",{originalErrorMessage:b==null?void 0:b.message})}E=_.entries,P=_.state}if(P==="INSTANCE_STATE_UNSPECIFIED"?f=500:P==="NO_CHANGE"?f=304:(P==="NO_TEMPLATE"||P==="EMPTY_CONFIG")&&(E={}),f!==304&&f!==200)throw p.create("fetch-status",{httpStatus:f});return{status:f,eTag:g,config:E}}}/**
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
 */function Ta(e,t){return new Promise((n,a)=>{const r=Math.max(t-Date.now(),0),s=setTimeout(n,r);e.addEventListener(()=>{clearTimeout(s),a(p.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function Da(e){if(!(e instanceof D)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Aa{constructor(t,n){this.client=t,this.storage=n}async fetch(t){const n=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,n)}async attemptFetch(t,{throttleEndTimeMillis:n,backoffCount:a}){await Ta(t.signal,n);try{const r=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),r}catch(r){if(!Da(r))throw r;const s={throttleEndTimeMillis:Date.now()+ee(a),backoffCount:a+1};return await this.storage.setThrottleMetadata(s),this.attemptFetch(t,s)}}}/**
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
 */const Oa=60*1e3,Ra=12*60*60*1e3;class La{constructor(t,n,a,r,s){this.app=t,this._client=n,this._storageCache=a,this._storage=r,this._logger=s,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:Oa,minimumFetchIntervalMillis:Ra},this.defaultConfig={}}get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}}/**
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
 */function x(e,t){const n=e.target.error||void 0;return p.create(t,{originalErrorMessage:n&&(n==null?void 0:n.message)})}const A="app_namespace_store",Ma="firebase_remote_config",Fa=1;function ka(){return new Promise((e,t)=>{try{const n=indexedDB.open(Ma,Fa);n.onerror=a=>{t(x(a,"storage-open"))},n.onsuccess=a=>{e(a.target.result)},n.onupgradeneeded=a=>{const r=a.target.result;switch(a.oldVersion){case 0:r.createObjectStore(A,{keyPath:"compositeKey"})}}}catch(n){t(p.create("storage-open",{originalErrorMessage:n==null?void 0:n.message}))}})}class Pa{constructor(t,n,a,r=ka()){this.appId=t,this.appName=n,this.namespace=a,this.openDbPromise=r}getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}async get(t){const n=await this.openDbPromise;return new Promise((a,r)=>{const i=n.transaction([A],"readonly").objectStore(A),c=this.createCompositeKey(t);try{const o=i.get(c);o.onerror=l=>{r(x(l,"storage-get"))},o.onsuccess=l=>{const d=l.target.result;a(d?d.value:void 0)}}catch(o){r(p.create("storage-get",{originalErrorMessage:o==null?void 0:o.message}))}})}async set(t,n){const a=await this.openDbPromise;return new Promise((r,s)=>{const c=a.transaction([A],"readwrite").objectStore(A),o=this.createCompositeKey(t);try{const l=c.put({compositeKey:o,value:n});l.onerror=d=>{s(x(d,"storage-set"))},l.onsuccess=()=>{r()}}catch(l){s(p.create("storage-set",{originalErrorMessage:l==null?void 0:l.message}))}})}async delete(t){const n=await this.openDbPromise;return new Promise((a,r)=>{const i=n.transaction([A],"readwrite").objectStore(A),c=this.createCompositeKey(t);try{const o=i.delete(c);o.onerror=l=>{r(x(l,"storage-delete"))},o.onsuccess=()=>{a()}}catch(o){r(p.create("storage-delete",{originalErrorMessage:o==null?void 0:o.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}/**
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
 */class Na{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),n=this.storage.getLastSuccessfulFetchTimestampMillis(),a=this.storage.getActiveConfig(),r=await t;r&&(this.lastFetchStatus=r);const s=await n;s&&(this.lastSuccessfulFetchTimestampMillis=s);const i=await a;i&&(this.activeConfig=i)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}}/**
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
 */function va(){T(new S(Ia,e,"PUBLIC").setMultipleInstances(!0)),I(Z,$e),I(Z,$e,"esm2017");function e(t,{instanceIdentifier:n}){const a=t.getProvider("app").getImmediate(),r=t.getProvider("installations-internal").getImmediate();if(typeof window>"u")throw p.create("registration-window");if(!oe())throw p.create("indexed-db-unavailable");const{projectId:s,apiKey:i,appId:c}=a.options;if(!s)throw p.create("registration-project-id");if(!i)throw p.create("registration-api-key");if(!c)throw p.create("registration-app-id");n=n||"firebase";const o=new Pa(c,a.name,n),l=new Na(o),d=new ce(Z);d.logLevel=u.ERROR;const h=new Sa(r,Nn,n,s,i,c),f=new Aa(h,o),g=new wa(f,o,l,d),E=new La(a,g,l,o,d);return ba(E),E}}va();const Tt=k.createContext({});function xe({children:e}){const[t,n]=k.useState();return R.jsx(Tt.Provider,{value:{logEvent:t,setLogEvent:n},children:e})}try{xe.displayName="AnalyticsContextProvider",xe.__docgenInfo={description:"",displayName:"AnalyticsContextProvider",props:{}}}catch{}const Ba=k.createContext({remoteConfig:null,setRemoteConfig:null,remoteConfigData:null,setRemoteConfigData:null});function Ke({children:e}){const[t,n]=k.useState(null),[a,r]=k.useState(null);return R.jsx(Ba.Provider,{value:{remoteConfig:t,setRemoteConfig:n,remoteConfigData:a,setRemoteConfigData:r},children:e})}try{Ke.displayName="RemoteContextProvider",Ke.__docgenInfo={description:"",displayName:"RemoteContextProvider",props:{}}}catch{}function $a(){return k.useContext(Tt)}const je={"help-link":"_help-link_9okj2_2","help-link-text":"_help-link-text_9okj2_10"},xa=()=>{const{logEvent:e}=$a();return R.jsxs("a",{onClick:()=>e==null?void 0:e(Ge.CLICKED_HELP_LINK,{from:location.pathname}),className:je["help-link"],href:"https://aide.passculture.app/hc/fr/articles/4411991940369--Acteurs-culturels-Comment-poster-une-offre-%C3%A0-destination-d-un-groupe-scolaire-",rel:"noreferrer",target:"_blank",children:[R.jsx(Ot,{src:At,alt:"",width:"42"}),R.jsx("span",{className:je["help-link-text"],children:"Aide"})]})},Dt=xa,qa={title:"components/HelpLink",component:Dt},Ka=e=>R.jsx("div",{style:{width:500,height:500},children:R.jsx(Dt,{...e})}),$=Ka.bind({});var He,Ve,Ue;$.parameters={...$.parameters,docs:{...(He=$.parameters)==null?void 0:He.docs,source:{originalSource:`args => <div style={{
  width: 500,
  height: 500
}}>
    <HelpLink {...args} />
  </div>`,...(Ue=(Ve=$.parameters)==null?void 0:Ve.docs)==null?void 0:Ue.source}}};const za=["Default"];export{$ as Default,za as __namedExportsOrder,qa as default};
//# sourceMappingURL=HelpLink.stories-d970a1d5.js.map
