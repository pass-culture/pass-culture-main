import{r as _t}from"./iframe-BFYw_onD.js";import"./config-BqmKEuqZ.js";import{u as It}from"./chunk-NISHYRIK-g2e0ZoVv.js";/**
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
 */const bt={SDK_VERSION:"${JSCORE_VERSION}"};/**
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
 */const X=function(t,e){if(!t)throw wt(e)},wt=function(t){return new Error("Firebase Database ("+bt.SDK_VERSION+") INTERNAL ASSERT FAILED: "+t)};/**
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
 */const Ke=function(t){const e=[];let a=0;for(let n=0;n<t.length;n++){let s=t.charCodeAt(n);s<128?e[a++]=s:s<2048?(e[a++]=s>>6|192,e[a++]=s&63|128):(s&64512)===55296&&n+1<t.length&&(t.charCodeAt(n+1)&64512)===56320?(s=65536+((s&1023)<<10)+(t.charCodeAt(++n)&1023),e[a++]=s>>18|240,e[a++]=s>>12&63|128,e[a++]=s>>6&63|128,e[a++]=s&63|128):(e[a++]=s>>12|224,e[a++]=s>>6&63|128,e[a++]=s&63|128)}return e},St=function(t){const e=[];let a=0,n=0;for(;a<t.length;){const s=t[a++];if(s<128)e[n++]=String.fromCharCode(s);else if(s>191&&s<224){const i=t[a++];e[n++]=String.fromCharCode((s&31)<<6|i&63)}else if(s>239&&s<365){const i=t[a++],r=t[a++],o=t[a++],c=((s&7)<<18|(i&63)<<12|(r&63)<<6|o&63)-65536;e[n++]=String.fromCharCode(55296+(c>>10)),e[n++]=String.fromCharCode(56320+(c&1023))}else{const i=t[a++],r=t[a++];e[n++]=String.fromCharCode((s&15)<<12|(i&63)<<6|r&63)}}return e.join("")},Tt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(t,e){if(!Array.isArray(t))throw Error("encodeByteArray takes an array as a parameter");this.init_();const a=e?this.byteToCharMapWebSafe_:this.byteToCharMap_,n=[];for(let s=0;s<t.length;s+=3){const i=t[s],r=s+1<t.length,o=r?t[s+1]:0,c=s+2<t.length,l=c?t[s+2]:0,f=i>>2,h=(i&3)<<4|o>>4;let u=(o&15)<<2|l>>6,_=l&63;c||(_=64,r||(u=64)),n.push(a[f],a[h],a[u],a[_])}return n.join("")},encodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?btoa(t):this.encodeByteArray(Ke(t),e)},decodeString(t,e){return this.HAS_NATIVE_SUPPORT&&!e?atob(t):St(this.decodeStringToByteArray(t,e))},decodeStringToByteArray(t,e){this.init_();const a=e?this.charToByteMapWebSafe_:this.charToByteMap_,n=[];for(let s=0;s<t.length;){const i=a[t.charAt(s++)],o=s<t.length?a[t.charAt(s)]:0;++s;const l=s<t.length?a[t.charAt(s)]:64;++s;const h=s<t.length?a[t.charAt(s)]:64;if(++s,i==null||o==null||l==null||h==null)throw new yt;const u=i<<2|o>>4;if(n.push(u),l!==64){const _=o<<4&240|l>>2;if(n.push(_),h!==64){const I=l<<6&192|h;n.push(I)}}}return n},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let t=0;t<this.ENCODED_VALS.length;t++)this.byteToCharMap_[t]=this.ENCODED_VALS.charAt(t),this.charToByteMap_[this.byteToCharMap_[t]]=t,this.byteToCharMapWebSafe_[t]=this.ENCODED_VALS_WEBSAFE.charAt(t),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[t]]=t,t>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(t)]=t,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(t)]=t)}}};class yt extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const At=function(t){const e=Ke(t);return Tt.encodeByteArray(e,!0)},He=function(t){return At(t).replace(/\./g,"")};function Dt(){const t=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof t=="object"&&t.id!==void 0}function te(){try{return typeof indexedDB=="object"}catch{return!1}}function Ve(){return new Promise((t,e)=>{try{let a=!0;const n="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(n);s.onsuccess=()=>{s.result.close(),a||self.indexedDB.deleteDatabase(n),t(!0)},s.onupgradeneeded=()=>{a=!1},s.onerror=()=>{e(s.error?.message||"")}}catch(a){e(a)}})}function Rt(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const Ot="FirebaseError";class A extends Error{constructor(e,a,n){super(a),this.code=e,this.customData=n,this.name=Ot,Object.setPrototypeOf(this,A.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,P.prototype.create)}}class P{constructor(e,a,n){this.service=e,this.serviceName=a,this.errors=n}create(e,...a){const n=a[0]||{},s=`${this.service}/${e}`,i=this.errors[e],r=i?Lt(i,n):"Error",o=`${this.serviceName}: ${r} (${s}).`;return new A(s,o,n)}}function Lt(t,e){return t.replace(kt,(a,n)=>{const s=e[n];return s!=null?String(s):`<${n}?>`})}const kt=/\{\$([^}]+)}/g;/**
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
 */const Mt=1e3,Ft=2,Nt=4*60*60*1e3,Pt=.5;function v(t,e=Mt,a=Ft){const n=e*Math.pow(a,t),s=Math.round(Pt*n*(Math.random()-.5)*2);return Math.min(Nt,n+s)}/**
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
 */function Ue(t){return t&&t._delegate?t._delegate:t}class T{constructor(e,a,n){this.name=e,this.instanceFactory=a,this.type=n,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(e){return this.instantiationMode=e,this}setMultipleInstances(e){return this.multipleInstances=e,this}setServiceProps(e){return this.serviceProps=e,this}setInstanceCreatedCallback(e){return this.onInstanceCreated=e,this}}/**
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
 */var d;(function(t){t[t.DEBUG=0]="DEBUG",t[t.VERBOSE=1]="VERBOSE",t[t.INFO=2]="INFO",t[t.WARN=3]="WARN",t[t.ERROR=4]="ERROR",t[t.SILENT=5]="SILENT"})(d||(d={}));const Bt={debug:d.DEBUG,verbose:d.VERBOSE,info:d.INFO,warn:d.WARN,error:d.ERROR,silent:d.SILENT},vt=d.INFO,$t={[d.DEBUG]:"log",[d.VERBOSE]:"log",[d.INFO]:"info",[d.WARN]:"warn",[d.ERROR]:"error"},Kt=(t,e,...a)=>{if(e<t.logLevel)return;const n=new Date().toISOString(),s=$t[e];if(s)console[s](`[${n}]  ${t.name}:`,...a);else throw new Error(`Attempted to log a message with an invalid logType (value: ${e})`)};class ae{constructor(e){this.name=e,this._logLevel=vt,this._logHandler=Kt,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(e){if(!(e in d))throw new TypeError(`Invalid value "${e}" assigned to \`logLevel\``);this._logLevel=e}setLogLevel(e){this._logLevel=typeof e=="string"?Bt[e]:e}get logHandler(){return this._logHandler}set logHandler(e){if(typeof e!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=e}get userLogHandler(){return this._userLogHandler}set userLogHandler(e){this._userLogHandler=e}debug(...e){this._userLogHandler&&this._userLogHandler(this,d.DEBUG,...e),this._logHandler(this,d.DEBUG,...e)}log(...e){this._userLogHandler&&this._userLogHandler(this,d.VERBOSE,...e),this._logHandler(this,d.VERBOSE,...e)}info(...e){this._userLogHandler&&this._userLogHandler(this,d.INFO,...e),this._logHandler(this,d.INFO,...e)}warn(...e){this._userLogHandler&&this._userLogHandler(this,d.WARN,...e),this._logHandler(this,d.WARN,...e)}error(...e){this._userLogHandler&&this._userLogHandler(this,d.ERROR,...e),this._logHandler(this,d.ERROR,...e)}}const Ht=(t,e)=>e.some(a=>t instanceof a);let ue,fe;function Vt(){return ue||(ue=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Ut(){return fe||(fe=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const xe=new WeakMap,J=new WeakMap,je=new WeakMap,V=new WeakMap,ne=new WeakMap;function xt(t){const e=new Promise((a,n)=>{const s=()=>{t.removeEventListener("success",i),t.removeEventListener("error",r)},i=()=>{a(S(t.result)),s()},r=()=>{n(t.error),s()};t.addEventListener("success",i),t.addEventListener("error",r)});return e.then(a=>{a instanceof IDBCursor&&xe.set(a,t)}).catch(()=>{}),ne.set(e,t),e}function jt(t){if(J.has(t))return;const e=new Promise((a,n)=>{const s=()=>{t.removeEventListener("complete",i),t.removeEventListener("error",r),t.removeEventListener("abort",r)},i=()=>{a(),s()},r=()=>{n(t.error||new DOMException("AbortError","AbortError")),s()};t.addEventListener("complete",i),t.addEventListener("error",r),t.addEventListener("abort",r)});J.set(t,e)}let Q={get(t,e,a){if(t instanceof IDBTransaction){if(e==="done")return J.get(t);if(e==="objectStoreNames")return t.objectStoreNames||je.get(t);if(e==="store")return a.objectStoreNames[1]?void 0:a.objectStore(a.objectStoreNames[0])}return S(t[e])},set(t,e,a){return t[e]=a,!0},has(t,e){return t instanceof IDBTransaction&&(e==="done"||e==="store")?!0:e in t}};function Gt(t){Q=t(Q)}function Wt(t){return t===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(e,...a){const n=t.call(U(this),e,...a);return je.set(n,e.sort?e.sort():[e]),S(n)}:Ut().includes(t)?function(...e){return t.apply(U(this),e),S(xe.get(this))}:function(...e){return S(t.apply(U(this),e))}}function qt(t){return typeof t=="function"?Wt(t):(t instanceof IDBTransaction&&jt(t),Ht(t,Vt())?new Proxy(t,Q):t)}function S(t){if(t instanceof IDBRequest)return xt(t);if(V.has(t))return V.get(t);const e=qt(t);return e!==t&&(V.set(t,e),ne.set(e,t)),e}const U=t=>ne.get(t);function Ge(t,e,{blocked:a,upgrade:n,blocking:s,terminated:i}={}){const r=indexedDB.open(t,e),o=S(r);return n&&r.addEventListener("upgradeneeded",c=>{n(S(r.result),c.oldVersion,c.newVersion,S(r.transaction),c)}),a&&r.addEventListener("blocked",c=>a(c.oldVersion,c.newVersion,c)),o.then(c=>{i&&c.addEventListener("close",()=>i()),s&&c.addEventListener("versionchange",l=>s(l.oldVersion,l.newVersion,l))}).catch(()=>{}),o}const zt=["get","getKey","getAll","getAllKeys","count"],Yt=["put","add","delete","clear"],x=new Map;function ge(t,e){if(!(t instanceof IDBDatabase&&!(e in t)&&typeof e=="string"))return;if(x.get(e))return x.get(e);const a=e.replace(/FromIndex$/,""),n=e!==a,s=Yt.includes(a);if(!(a in(n?IDBIndex:IDBObjectStore).prototype)||!(s||zt.includes(a)))return;const i=async function(r,...o){const c=this.transaction(r,s?"readwrite":"readonly");let l=c.store;return n&&(l=l.index(o.shift())),(await Promise.all([l[a](...o),s&&c.done]))[0]};return x.set(e,i),i}Gt(t=>({...t,get:(e,a,n)=>ge(e,a)||t.get(e,a,n),has:(e,a)=>!!ge(e,a)||t.has(e,a)}));/**
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
 */class Xt{constructor(e){this.container=e}getPlatformInfoString(){return this.container.getProviders().map(a=>{if(Jt(a)){const n=a.getImmediate();return`${n.library}/${n.version}`}else return null}).filter(a=>a).join(" ")}}function Jt(t){return t.getComponent()?.type==="VERSION"}const Z="@firebase/app",me="0.14.3";/**
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
 */const E=new ae("@firebase/app"),Qt="@firebase/app-compat",Zt="@firebase/analytics-compat",ea="@firebase/analytics",ta="@firebase/app-check-compat",aa="@firebase/app-check",na="@firebase/auth",sa="@firebase/auth-compat",ia="@firebase/database",ra="@firebase/data-connect",oa="@firebase/database-compat",ca="@firebase/functions",la="@firebase/functions-compat",ha="@firebase/installations",da="@firebase/installations-compat",ua="@firebase/messaging",fa="@firebase/messaging-compat",ga="@firebase/performance",ma="@firebase/performance-compat",pa="@firebase/remote-config",Ca="@firebase/remote-config-compat",Ea="@firebase/storage",_a="@firebase/storage-compat",Ia="@firebase/firestore",ba="@firebase/ai",wa="@firebase/firestore-compat",Sa="firebase",Ta="12.3.0",ya={[Z]:"fire-core",[Qt]:"fire-core-compat",[ea]:"fire-analytics",[Zt]:"fire-analytics-compat",[aa]:"fire-app-check",[ta]:"fire-app-check-compat",[na]:"fire-auth",[sa]:"fire-auth-compat",[ia]:"fire-rtdb",[ra]:"fire-data-connect",[oa]:"fire-rtdb-compat",[ca]:"fire-fn",[la]:"fire-fn-compat",[ha]:"fire-iid",[da]:"fire-iid-compat",[ua]:"fire-fcm",[fa]:"fire-fcm-compat",[ga]:"fire-perf",[ma]:"fire-perf-compat",[pa]:"fire-rc",[Ca]:"fire-rc-compat",[Ea]:"fire-gcs",[_a]:"fire-gcs-compat",[Ia]:"fire-fst",[wa]:"fire-fst-compat",[ba]:"fire-vertex","fire-js":"fire-js",[Sa]:"fire-js-all"};/**
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
 */const Aa=new Map,Da=new Map,pe=new Map;function Ce(t,e){try{t.container.addComponent(e)}catch(a){E.debug(`Component ${e.name} failed to register with FirebaseApp ${t.name}`,a)}}function y(t){const e=t.name;if(pe.has(e))return E.debug(`There were multiple attempts to register component ${e}.`),!1;pe.set(e,t);for(const a of Aa.values())Ce(a,t);for(const a of Da.values())Ce(a,t);return!0}function We(t,e){const a=t.container.getProvider("heartbeat").getImmediate({optional:!0});return a&&a.triggerHeartbeat(),t.container.getProvider(e)}/**
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
 */const Ra={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},se=new P("app","Firebase",Ra);/**
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
 */const Ee=Ta;function C(t,e,a){let n=ya[t]??t;a&&(n+=`-${a}`);const s=n.match(/\s|\//),i=e.match(/\s|\//);if(s||i){const r=[`Unable to register library "${n}" with version "${e}":`];s&&r.push(`library name "${n}" contains illegal characters (whitespace or "/")`),s&&i&&r.push("and"),i&&r.push(`version name "${e}" contains illegal characters (whitespace or "/")`),E.warn(r.join(" "));return}y(new T(`${n}-version`,()=>({library:n,version:e}),"VERSION"))}/**
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
 */const Oa="firebase-heartbeat-database",La=1,N="firebase-heartbeat-store";let j=null;function qe(){return j||(j=Ge(Oa,La,{upgrade:(t,e)=>{switch(e){case 0:try{t.createObjectStore(N)}catch(a){console.warn(a)}}}}).catch(t=>{throw se.create("idb-open",{originalErrorMessage:t.message})})),j}async function ka(t){try{const a=(await qe()).transaction(N),n=await a.objectStore(N).get(ze(t));return await a.done,n}catch(e){if(e instanceof A)E.warn(e.message);else{const a=se.create("idb-get",{originalErrorMessage:e?.message});E.warn(a.message)}}}async function _e(t,e){try{const n=(await qe()).transaction(N,"readwrite");await n.objectStore(N).put(e,ze(t)),await n.done}catch(a){if(a instanceof A)E.warn(a.message);else{const n=se.create("idb-set",{originalErrorMessage:a?.message});E.warn(n.message)}}}function ze(t){return`${t.name}!${t.options.appId}`}/**
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
 */const Ma=1024,Fa=30;class Na{constructor(e){this.container=e,this._heartbeatsCache=null;const a=this.container.getProvider("app").getImmediate();this._storage=new Ba(a),this._heartbeatsCachePromise=this._storage.read().then(n=>(this._heartbeatsCache=n,n))}async triggerHeartbeat(){try{const a=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),n=Ie();if(this._heartbeatsCache?.heartbeats==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,this._heartbeatsCache?.heartbeats==null)||this._heartbeatsCache.lastSentHeartbeatDate===n||this._heartbeatsCache.heartbeats.some(s=>s.date===n))return;if(this._heartbeatsCache.heartbeats.push({date:n,agent:a}),this._heartbeatsCache.heartbeats.length>Fa){const s=va(this._heartbeatsCache.heartbeats);this._heartbeatsCache.heartbeats.splice(s,1)}return this._storage.overwrite(this._heartbeatsCache)}catch(e){E.warn(e)}}async getHeartbeatsHeader(){try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,this._heartbeatsCache?.heartbeats==null||this._heartbeatsCache.heartbeats.length===0)return"";const e=Ie(),{heartbeatsToSend:a,unsentEntries:n}=Pa(this._heartbeatsCache.heartbeats),s=He(JSON.stringify({version:2,heartbeats:a}));return this._heartbeatsCache.lastSentHeartbeatDate=e,n.length>0?(this._heartbeatsCache.heartbeats=n,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),s}catch(e){return E.warn(e),""}}}function Ie(){return new Date().toISOString().substring(0,10)}function Pa(t,e=Ma){const a=[];let n=t.slice();for(const s of t){const i=a.find(r=>r.agent===s.agent);if(i){if(i.dates.push(s.date),be(a)>e){i.dates.pop();break}}else if(a.push({agent:s.agent,dates:[s.date]}),be(a)>e){a.pop();break}n=n.slice(1)}return{heartbeatsToSend:a,unsentEntries:n}}class Ba{constructor(e){this.app=e,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return te()?Ve().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const a=await ka(this.app);return a?.heartbeats?a:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(e){if(await this._canUseIndexedDBPromise){const n=await this.read();return _e(this.app,{lastSentHeartbeatDate:e.lastSentHeartbeatDate??n.lastSentHeartbeatDate,heartbeats:e.heartbeats})}else return}async add(e){if(await this._canUseIndexedDBPromise){const n=await this.read();return _e(this.app,{lastSentHeartbeatDate:e.lastSentHeartbeatDate??n.lastSentHeartbeatDate,heartbeats:[...n.heartbeats,...e.heartbeats]})}else return}}function be(t){return He(JSON.stringify({version:2,heartbeats:t})).length}function va(t){if(t.length===0)return-1;let e=0,a=t[0].date;for(let n=1;n<t.length;n++)t[n].date<a&&(a=t[n].date,e=n);return e}/**
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
 */function $a(t){y(new T("platform-logger",e=>new Xt(e),"PRIVATE")),y(new T("heartbeat",e=>new Na(e),"PRIVATE")),C(Z,me,t),C(Z,me,"esm2020"),C("fire-js","")}$a("");const Ye="@firebase/installations",ie="0.6.19";/**
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
 */const Xe=1e4,Je=`w:${ie}`,Qe="FIS_v2",Ka="https://firebaseinstallations.googleapis.com/v1",Ha=60*60*1e3,Va="installations",Ua="Installations";/**
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
 */const xa={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},O=new P(Va,Ua,xa);function Ze(t){return t instanceof A&&t.code.includes("request-failed")}/**
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
 */function et({projectId:t}){return`${Ka}/projects/${t}/installations`}function tt(t){return{token:t.token,requestStatus:2,expiresIn:Ga(t.expiresIn),creationTime:Date.now()}}async function at(t,e){const n=(await e.json()).error;return O.create("request-failed",{requestName:t,serverCode:n.code,serverMessage:n.message,serverStatus:n.status})}function nt({apiKey:t}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":t})}function ja(t,{refreshToken:e}){const a=nt(t);return a.append("Authorization",Wa(e)),a}async function st(t){const e=await t();return e.status>=500&&e.status<600?t():e}function Ga(t){return Number(t.replace("s","000"))}function Wa(t){return`${Qe} ${t}`}/**
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
 */async function qa({appConfig:t,heartbeatServiceProvider:e},{fid:a}){const n=et(t),s=nt(t),i=e.getImmediate({optional:!0});if(i){const l=await i.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const r={fid:a,authVersion:Qe,appId:t.appId,sdkVersion:Je},o={method:"POST",headers:s,body:JSON.stringify(r)},c=await st(()=>fetch(n,o));if(c.ok){const l=await c.json();return{fid:l.fid||a,registrationStatus:2,refreshToken:l.refreshToken,authToken:tt(l.authToken)}}else throw await at("Create Installation",c)}/**
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
 */function it(t){return new Promise(e=>{setTimeout(e,t)})}/**
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
 */function za(t){return btoa(String.fromCharCode(...t)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const Ya=/^[cdef][\w-]{21}$/,ee="";function Xa(){try{const t=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(t),t[0]=112+t[0]%16;const a=Ja(t);return Ya.test(a)?a:ee}catch{return ee}}function Ja(t){return za(t).substr(0,22)}/**
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
 */function K(t){return`${t.appName}!${t.appId}`}/**
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
 */const rt=new Map;function ot(t,e){const a=K(t);ct(a,e),Qa(a,e)}function ct(t,e){const a=rt.get(t);if(a)for(const n of a)n(e)}function Qa(t,e){const a=Za();a&&a.postMessage({key:t,fid:e}),en()}let R=null;function Za(){return!R&&"BroadcastChannel"in self&&(R=new BroadcastChannel("[Firebase] FID Change"),R.onmessage=t=>{ct(t.data.key,t.data.fid)}),R}function en(){rt.size===0&&R&&(R.close(),R=null)}/**
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
 */const tn="firebase-installations-database",an=1,L="firebase-installations-store";let G=null;function re(){return G||(G=Ge(tn,an,{upgrade:(t,e)=>{switch(e){case 0:t.createObjectStore(L)}}})),G}async function $(t,e){const a=K(t),s=(await re()).transaction(L,"readwrite"),i=s.objectStore(L),r=await i.get(a);return await i.put(e,a),await s.done,(!r||r.fid!==e.fid)&&ot(t,e.fid),e}async function lt(t){const e=K(t),n=(await re()).transaction(L,"readwrite");await n.objectStore(L).delete(e),await n.done}async function H(t,e){const a=K(t),s=(await re()).transaction(L,"readwrite"),i=s.objectStore(L),r=await i.get(a),o=e(r);return o===void 0?await i.delete(a):await i.put(o,a),await s.done,o&&(!r||r.fid!==o.fid)&&ot(t,o.fid),o}/**
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
 */async function oe(t){let e;const a=await H(t.appConfig,n=>{const s=nn(n),i=sn(t,s);return e=i.registrationPromise,i.installationEntry});return a.fid===ee?{installationEntry:await e}:{installationEntry:a,registrationPromise:e}}function nn(t){const e=t||{fid:Xa(),registrationStatus:0};return ht(e)}function sn(t,e){if(e.registrationStatus===0){if(!navigator.onLine){const s=Promise.reject(O.create("app-offline"));return{installationEntry:e,registrationPromise:s}}const a={fid:e.fid,registrationStatus:1,registrationTime:Date.now()},n=rn(t,a);return{installationEntry:a,registrationPromise:n}}else return e.registrationStatus===1?{installationEntry:e,registrationPromise:on(t)}:{installationEntry:e}}async function rn(t,e){try{const a=await qa(t,e);return $(t.appConfig,a)}catch(a){throw Ze(a)&&a.customData.serverCode===409?await lt(t.appConfig):await $(t.appConfig,{fid:e.fid,registrationStatus:0}),a}}async function on(t){let e=await we(t.appConfig);for(;e.registrationStatus===1;)await it(100),e=await we(t.appConfig);if(e.registrationStatus===0){const{installationEntry:a,registrationPromise:n}=await oe(t);return n||a}return e}function we(t){return H(t,e=>{if(!e)throw O.create("installation-not-found");return ht(e)})}function ht(t){return cn(t)?{fid:t.fid,registrationStatus:0}:t}function cn(t){return t.registrationStatus===1&&t.registrationTime+Xe<Date.now()}/**
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
 */async function ln({appConfig:t,heartbeatServiceProvider:e},a){const n=hn(t,a),s=ja(t,a),i=e.getImmediate({optional:!0});if(i){const l=await i.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const r={installation:{sdkVersion:Je,appId:t.appId}},o={method:"POST",headers:s,body:JSON.stringify(r)},c=await st(()=>fetch(n,o));if(c.ok){const l=await c.json();return tt(l)}else throw await at("Generate Auth Token",c)}function hn(t,{fid:e}){return`${et(t)}/${e}/authTokens:generate`}/**
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
 */async function ce(t,e=!1){let a;const n=await H(t.appConfig,i=>{if(!dt(i))throw O.create("not-registered");const r=i.authToken;if(!e&&fn(r))return i;if(r.requestStatus===1)return a=dn(t,e),i;{if(!navigator.onLine)throw O.create("app-offline");const o=mn(i);return a=un(t,o),o}});return a?await a:n.authToken}async function dn(t,e){let a=await Se(t.appConfig);for(;a.authToken.requestStatus===1;)await it(100),a=await Se(t.appConfig);const n=a.authToken;return n.requestStatus===0?ce(t,e):n}function Se(t){return H(t,e=>{if(!dt(e))throw O.create("not-registered");const a=e.authToken;return pn(a)?{...e,authToken:{requestStatus:0}}:e})}async function un(t,e){try{const a=await ln(t,e),n={...e,authToken:a};return await $(t.appConfig,n),a}catch(a){if(Ze(a)&&(a.customData.serverCode===401||a.customData.serverCode===404))await lt(t.appConfig);else{const n={...e,authToken:{requestStatus:0}};await $(t.appConfig,n)}throw a}}function dt(t){return t!==void 0&&t.registrationStatus===2}function fn(t){return t.requestStatus===2&&!gn(t)}function gn(t){const e=Date.now();return e<t.creationTime||t.creationTime+t.expiresIn<e+Ha}function mn(t){const e={requestStatus:1,requestTime:Date.now()};return{...t,authToken:e}}function pn(t){return t.requestStatus===1&&t.requestTime+Xe<Date.now()}/**
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
 */async function Cn(t){const e=t,{installationEntry:a,registrationPromise:n}=await oe(e);return n?n.catch(console.error):ce(e).catch(console.error),a.fid}/**
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
 */async function En(t,e=!1){const a=t;return await _n(a),(await ce(a,e)).token}async function _n(t){const{registrationPromise:e}=await oe(t);e&&await e}/**
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
 */function In(t){if(!t||!t.options)throw W("App Configuration");if(!t.name)throw W("App Name");const e=["projectId","apiKey","appId"];for(const a of e)if(!t.options[a])throw W(a);return{appName:t.name,projectId:t.options.projectId,apiKey:t.options.apiKey,appId:t.options.appId}}function W(t){return O.create("missing-app-config-values",{valueName:t})}/**
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
 */const ut="installations",bn="installations-internal",wn=t=>{const e=t.getProvider("app").getImmediate(),a=In(e),n=We(e,"heartbeat");return{app:e,appConfig:a,heartbeatServiceProvider:n,_delete:()=>Promise.resolve()}},Sn=t=>{const e=t.getProvider("app").getImmediate(),a=We(e,ut).getImmediate();return{getId:()=>Cn(a),getToken:s=>En(a,s)}};function Tn(){y(new T(ut,wn,"PUBLIC")),y(new T(bn,Sn,"PRIVATE"))}Tn();C(Ye,ie);C(Ye,ie,"esm2020");/**
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
 */const Te="analytics",yn="firebase_id",An="origin",Dn=60*1e3,Rn="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",le="https://www.googletagmanager.com/gtag/js";/**
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
 */const m=new ae("@firebase/analytics");/**
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
 */const On={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-initialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},p=new P("analytics","Analytics",On);/**
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
 */function Ln(t){if(!t.startsWith(le)){const e=p.create("invalid-gtag-resource",{gtagURL:t});return m.warn(e.message),""}return t}function ft(t){return Promise.all(t.map(e=>e.catch(a=>a)))}function kn(t,e){let a;return window.trustedTypes&&(a=window.trustedTypes.createPolicy(t,e)),a}function Mn(t,e){const a=kn("firebase-js-sdk-policy",{createScriptURL:Ln}),n=document.createElement("script"),s=`${le}?l=${t}&id=${e}`;n.src=a?a?.createScriptURL(s):s,n.async=!0,document.head.appendChild(n)}function Fn(t){let e=[];return Array.isArray(window[t])?e=window[t]:window[t]=e,e}async function Nn(t,e,a,n,s,i){const r=n[s];try{if(r)await e[r];else{const c=(await ft(a)).find(l=>l.measurementId===s);c&&await e[c.appId]}}catch(o){m.error(o)}t("config",s,i)}async function Pn(t,e,a,n,s){try{let i=[];if(s&&s.send_to){let r=s.send_to;Array.isArray(r)||(r=[r]);const o=await ft(a);for(const c of r){const l=o.find(h=>h.measurementId===c),f=l&&e[l.appId];if(f)i.push(f);else{i=[];break}}}i.length===0&&(i=Object.values(e)),await Promise.all(i),t("event",n,s||{})}catch(i){m.error(i)}}function Bn(t,e,a,n){async function s(i,...r){try{if(i==="event"){const[o,c]=r;await Pn(t,e,a,o,c)}else if(i==="config"){const[o,c]=r;await Nn(t,e,a,n,o,c)}else if(i==="consent"){const[o,c]=r;t("consent",o,c)}else if(i==="get"){const[o,c,l]=r;t("get",o,c,l)}else if(i==="set"){const[o]=r;t("set",o)}else t(i,...r)}catch(o){m.error(o)}}return s}function vn(t,e,a,n,s){let i=function(...r){window[n].push(arguments)};return window[s]&&typeof window[s]=="function"&&(i=window[s]),window[s]=Bn(i,t,e,a),{gtagCore:i,wrappedGtag:window[s]}}function $n(t){const e=window.document.getElementsByTagName("script");for(const a of Object.values(e))if(a.src&&a.src.includes(le)&&a.src.includes(t))return a;return null}/**
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
 */const Kn=30,Hn=1e3;class Vn{constructor(e={},a=Hn){this.throttleMetadata=e,this.intervalMillis=a}getThrottleMetadata(e){return this.throttleMetadata[e]}setThrottleMetadata(e,a){this.throttleMetadata[e]=a}deleteThrottleMetadata(e){delete this.throttleMetadata[e]}}const gt=new Vn;function Un(t){return new Headers({Accept:"application/json","x-goog-api-key":t})}async function xn(t){const{appId:e,apiKey:a}=t,n={method:"GET",headers:Un(a)},s=Rn.replace("{app-id}",e),i=await fetch(s,n);if(i.status!==200&&i.status!==304){let r="";try{const o=await i.json();o.error?.message&&(r=o.error.message)}catch{}throw p.create("config-fetch-failed",{httpStatus:i.status,responseMessage:r})}return i.json()}async function jn(t,e=gt,a){const{appId:n,apiKey:s,measurementId:i}=t.options;if(!n)throw p.create("no-app-id");if(!s){if(i)return{measurementId:i,appId:n};throw p.create("no-api-key")}const r=e.getThrottleMetadata(n)||{backoffCount:0,throttleEndTimeMillis:Date.now()},o=new qn;return setTimeout(async()=>{o.abort()},Dn),mt({appId:n,apiKey:s,measurementId:i},r,o,e)}async function mt(t,{throttleEndTimeMillis:e,backoffCount:a},n,s=gt){const{appId:i,measurementId:r}=t;try{await Gn(n,e)}catch(o){if(r)return m.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${r} provided in the "measurementId" field in the local Firebase config. [${o?.message}]`),{appId:i,measurementId:r};throw o}try{const o=await xn(t);return s.deleteThrottleMetadata(i),o}catch(o){const c=o;if(!Wn(c)){if(s.deleteThrottleMetadata(i),r)return m.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${r} provided in the "measurementId" field in the local Firebase config. [${c?.message}]`),{appId:i,measurementId:r};throw o}const l=Number(c?.customData?.httpStatus)===503?v(a,s.intervalMillis,Kn):v(a,s.intervalMillis),f={throttleEndTimeMillis:Date.now()+l,backoffCount:a+1};return s.setThrottleMetadata(i,f),m.debug(`Calling attemptFetch again in ${l} millis`),mt(t,f,n,s)}}function Gn(t,e){return new Promise((a,n)=>{const s=Math.max(e-Date.now(),0),i=setTimeout(a,s);t.addEventListener(()=>{clearTimeout(i),n(p.create("fetch-throttle",{throttleEndTimeMillis:e}))})})}function Wn(t){if(!(t instanceof A)||!t.customData)return!1;const e=Number(t.customData.httpStatus);return e===429||e===500||e===503||e===504}class qn{constructor(){this.listeners=[]}addEventListener(e){this.listeners.push(e)}abort(){this.listeners.forEach(e=>e())}}async function zn(t,e,a,n,s){if(s&&s.global){t("event",a,n);return}else{const i=await e,r={...n,send_to:i};t("event",a,r)}}/**
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
 */async function Yn(){if(te())try{await Ve()}catch(t){return m.warn(p.create("indexeddb-unavailable",{errorInfo:t?.toString()}).message),!1}else return m.warn(p.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function Xn(t,e,a,n,s,i,r){const o=jn(t);o.then(u=>{a[u.measurementId]=u.appId,t.options.measurementId&&u.measurementId!==t.options.measurementId&&m.warn(`The measurement ID in the local Firebase config (${t.options.measurementId}) does not match the measurement ID fetched from the server (${u.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(u=>m.error(u)),e.push(o);const c=Yn().then(u=>{if(u)return n.getId()}),[l,f]=await Promise.all([o,c]);$n(i)||Mn(i,l.measurementId),s("js",new Date);const h=r?.config??{};return h[An]="firebase",h.update=!0,f!=null&&(h[yn]=f),s("config",l.measurementId,h),l.measurementId}/**
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
 */class Jn{constructor(e){this.app=e}_delete(){return delete F[this.app.options.appId],Promise.resolve()}}let F={},ye=[];const Ae={};let q="dataLayer",Qn="gtag",De,pt,Re=!1;function Zn(){const t=[];if(Dt()&&t.push("This is a browser extension environment."),Rt()||t.push("Cookies are not available."),t.length>0){const e=t.map((n,s)=>`(${s+1}) ${n}`).join(" "),a=p.create("invalid-analytics-context",{errorInfo:e});m.warn(a.message)}}function es(t,e,a){Zn();const n=t.options.appId;if(!n)throw p.create("no-app-id");if(!t.options.apiKey)if(t.options.measurementId)m.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${t.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw p.create("no-api-key");if(F[n]!=null)throw p.create("already-exists",{id:n});if(!Re){Fn(q);const{wrappedGtag:i,gtagCore:r}=vn(F,ye,Ae,q,Qn);pt=i,De=r,Re=!0}return F[n]=Xn(t,ye,Ae,e,De,q,a),new Jn(t)}function ts(t,e,a,n){t=Ue(t),zn(pt,F[t.app.options.appId],e,a,n).catch(s=>m.error(s))}const Oe="@firebase/analytics",Le="0.10.18";function as(){y(new T(Te,(e,{options:a})=>{const n=e.getProvider("app").getImmediate(),s=e.getProvider("installations-internal").getImmediate();return es(n,s,a)},"PUBLIC")),y(new T("analytics-internal",t,"PRIVATE")),C(Oe,Le),C(Oe,Le,"esm2020");function t(e){try{const a=e.getProvider(Te).getImmediate();return{logEvent:(n,s,i)=>ts(a,n,s,i)}}catch(a){throw p.create("interop-component-reg-failed",{reason:a})}}}as();const z="@firebase/remote-config",ke="0.7.0";/**
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
 */class ns{constructor(){this.listeners=[]}addEventListener(e){this.listeners.push(e)}abort(){this.listeners.forEach(e=>e())}}/**
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
 */const ss="remote-config",Me=100;/**
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
 */const is={"already-initialized":"Remote Config already initialized","registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser","custom-signal-max-allowed-signals":"Setting more than {$maxSignals} custom signals is not supported.","stream-error":"The stream was not able to connect to the backend: {$originalErrorMessage}.","realtime-unavailable":"The Realtime service is unavailable: {$originalErrorMessage}","update-message-invalid":"The stream invalidation message was unparsable: {$originalErrorMessage}","update-not-fetched":"Unable to fetch the latest config: {$originalErrorMessage}"},g=new P("remoteconfig","Remote Config",is);function rs(t){const e=Ue(t);return e._initializePromise||(e._initializePromise=e._storageCache.loadFromStorage().then(()=>{e._isInitializationComplete=!0})),e._initializePromise}/**
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
 */class os{constructor(e,a,n,s){this.client=e,this.storage=a,this.storageCache=n,this.logger=s}isCachedDataFresh(e,a){if(!a)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const n=Date.now()-a,s=n<=e;return this.logger.debug(`Config fetch cache check. Cache age millis: ${n}. Cache max age millis (minimumFetchIntervalMillis setting): ${e}. Is cache hit: ${s}.`),s}async fetch(e){const[a,n]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(n&&this.isCachedDataFresh(e.cacheMaxAgeMillis,a))return n;e.eTag=n&&n.eTag;const s=await this.client.fetch(e),i=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return s.status===200&&i.push(this.storage.setLastSuccessfulFetchResponse(s)),await Promise.all(i),s}}/**
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
 */function cs(t=navigator){return t.languages&&t.languages[0]||t.language}/**
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
 */class ls{constructor(e,a,n,s,i,r){this.firebaseInstallations=e,this.sdkVersion=a,this.namespace=n,this.projectId=s,this.apiKey=i,this.appId=r}async fetch(e){const[a,n]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),i=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,r={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":e.eTag||"*"},o={sdk_version:this.sdkVersion,app_instance_id:a,app_instance_id_token:n,app_id:this.appId,language_code:cs(),custom_signals:e.customSignals},c={method:"POST",headers:r,body:JSON.stringify(o)},l=fetch(i,c),f=new Promise((b,k)=>{e.signal.addEventListener(()=>{const de=new Error("The operation was aborted.");de.name="AbortError",k(de)})});let h;try{await Promise.race([l,f]),h=await l}catch(b){let k="fetch-client-network";throw b?.name==="AbortError"&&(k="fetch-timeout"),g.create(k,{originalErrorMessage:b?.message})}let u=h.status;const _=h.headers.get("ETag")||void 0;let I,D,M;if(h.status===200){let b;try{b=await h.json()}catch(k){throw g.create("fetch-client-parse",{originalErrorMessage:k?.message})}I=b.entries,D=b.state,M=b.templateVersion}if(D==="INSTANCE_STATE_UNSPECIFIED"?u=500:D==="NO_CHANGE"?u=304:(D==="NO_TEMPLATE"||D==="EMPTY_CONFIG")&&(I={}),u!==304&&u!==200)throw g.create("fetch-status",{httpStatus:u});return{status:u,eTag:_,config:I,templateVersion:M}}}/**
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
 */function hs(t,e){return new Promise((a,n)=>{const s=Math.max(e-Date.now(),0),i=setTimeout(a,s);t.addEventListener(()=>{clearTimeout(i),n(g.create("fetch-throttle",{throttleEndTimeMillis:e}))})})}function ds(t){if(!(t instanceof A)||!t.customData)return!1;const e=Number(t.customData.httpStatus);return e===429||e===500||e===503||e===504}class us{constructor(e,a){this.client=e,this.storage=a}async fetch(e){const a=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(e,a)}async attemptFetch(e,{throttleEndTimeMillis:a,backoffCount:n}){await hs(e.signal,a);try{const s=await this.client.fetch(e);return await this.storage.deleteThrottleMetadata(),s}catch(s){if(!ds(s))throw s;const i={throttleEndTimeMillis:Date.now()+v(n),backoffCount:n+1};return await this.storage.setThrottleMetadata(i),this.attemptFetch(e,i)}}}/**
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
 */const fs=60*1e3,gs=12*60*60*1e3;class ms{get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}constructor(e,a,n,s,i,r){this.app=e,this._client=a,this._storageCache=n,this._storage=s,this._logger=i,this._realtimeHandler=r,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:fs,minimumFetchIntervalMillis:gs},this.defaultConfig={}}}/**
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
 */function B(t,e){const a=t.target.error||void 0;return g.create(e,{originalErrorMessage:a&&a?.message})}const w="app_namespace_store",ps="firebase_remote_config",Cs=1;function Es(){return new Promise((t,e)=>{try{const a=indexedDB.open(ps,Cs);a.onerror=n=>{e(B(n,"storage-open"))},a.onsuccess=n=>{t(n.target.result)},a.onupgradeneeded=n=>{const s=n.target.result;switch(n.oldVersion){case 0:s.createObjectStore(w,{keyPath:"compositeKey"})}}}catch(a){e(g.create("storage-open",{originalErrorMessage:a?.message}))}})}class Ct{getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(e){return this.set("last_fetch_status",e)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(e){return this.set("last_successful_fetch_timestamp_millis",e)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(e){return this.set("last_successful_fetch_response",e)}getActiveConfig(){return this.get("active_config")}setActiveConfig(e){return this.set("active_config",e)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(e){return this.set("active_config_etag",e)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(e){return this.set("throttle_metadata",e)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}getCustomSignals(){return this.get("custom_signals")}getRealtimeBackoffMetadata(){return this.get("realtime_backoff_metadata")}setRealtimeBackoffMetadata(e){return this.set("realtime_backoff_metadata",e)}getActiveConfigTemplateVersion(){return this.get("last_known_template_version")}setActiveConfigTemplateVersion(e){return this.set("last_known_template_version",e)}}class _s extends Ct{constructor(e,a,n,s=Es()){super(),this.appId=e,this.appName=a,this.namespace=n,this.openDbPromise=s}async setCustomSignals(e){const n=(await this.openDbPromise).transaction([w],"readwrite"),s=await this.getWithTransaction("custom_signals",n),i=Et(e,s||{});return await this.setWithTransaction("custom_signals",i,n),i}async getWithTransaction(e,a){return new Promise((n,s)=>{const i=a.objectStore(w),r=this.createCompositeKey(e);try{const o=i.get(r);o.onerror=c=>{s(B(c,"storage-get"))},o.onsuccess=c=>{const l=c.target.result;n(l?l.value:void 0)}}catch(o){s(g.create("storage-get",{originalErrorMessage:o?.message}))}})}async setWithTransaction(e,a,n){return new Promise((s,i)=>{const r=n.objectStore(w),o=this.createCompositeKey(e);try{const c=r.put({compositeKey:o,value:a});c.onerror=l=>{i(B(l,"storage-set"))},c.onsuccess=()=>{s()}}catch(c){i(g.create("storage-set",{originalErrorMessage:c?.message}))}})}async get(e){const n=(await this.openDbPromise).transaction([w],"readonly");return this.getWithTransaction(e,n)}async set(e,a){const s=(await this.openDbPromise).transaction([w],"readwrite");return this.setWithTransaction(e,a,s)}async delete(e){const a=await this.openDbPromise;return new Promise((n,s)=>{const r=a.transaction([w],"readwrite").objectStore(w),o=this.createCompositeKey(e);try{const c=r.delete(o);c.onerror=l=>{s(B(l,"storage-delete"))},c.onsuccess=()=>{n()}}catch(c){s(g.create("storage-delete",{originalErrorMessage:c?.message}))}})}createCompositeKey(e){return[this.appId,this.appName,this.namespace,e].join()}}class Is extends Ct{constructor(){super(...arguments),this.storage={}}async get(e){return Promise.resolve(this.storage[e])}async set(e,a){return this.storage[e]=a,Promise.resolve(void 0)}async delete(e){return this.storage[e]=void 0,Promise.resolve()}async setCustomSignals(e){const a=this.storage.custom_signals||{};return this.storage.custom_signals=Et(e,a),Promise.resolve(this.storage.custom_signals)}}function Et(t,e){const a={...e,...t},n=Object.fromEntries(Object.entries(a).filter(([s,i])=>i!==null).map(([s,i])=>typeof i=="number"?[s,i.toString()]:[s,i]));if(Object.keys(n).length>Me)throw g.create("custom-signal-max-allowed-signals",{maxSignals:Me});return n}/**
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
 */class bs{constructor(e){this.storage=e}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}getCustomSignals(){return this.customSignals}async loadFromStorage(){const e=this.storage.getLastFetchStatus(),a=this.storage.getLastSuccessfulFetchTimestampMillis(),n=this.storage.getActiveConfig(),s=this.storage.getCustomSignals(),i=await e;i&&(this.lastFetchStatus=i);const r=await a;r&&(this.lastSuccessfulFetchTimestampMillis=r);const o=await n;o&&(this.activeConfig=o);const c=await s;c&&(this.customSignals=c)}setLastFetchStatus(e){return this.lastFetchStatus=e,this.storage.setLastFetchStatus(e)}setLastSuccessfulFetchTimestampMillis(e){return this.lastSuccessfulFetchTimestampMillis=e,this.storage.setLastSuccessfulFetchTimestampMillis(e)}setActiveConfig(e){return this.activeConfig=e,this.storage.setActiveConfig(e)}async setCustomSignals(e){this.customSignals=await this.storage.setCustomSignals(e)}}/**
 * @license
 * Copyright 2025 Google LLC
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
 */class ws{constructor(e){this.allowedEvents_=e,this.listeners_={},X(Array.isArray(e)&&e.length>0,"Requires a non-empty array")}trigger(e,...a){if(Array.isArray(this.listeners_[e])){const n=[...this.listeners_[e]];for(let s=0;s<n.length;s++)n[s].callback.apply(n[s].context,a)}}on(e,a,n){this.validateEventType_(e),this.listeners_[e]=this.listeners_[e]||[],this.listeners_[e].push({callback:a,context:n});const s=this.getInitialEvent(e);s&&a.apply(n,s)}off(e,a,n){this.validateEventType_(e);const s=this.listeners_[e]||[];for(let i=0;i<s.length;i++)if(s[i].callback===a&&(!n||n===s[i].context)){s.splice(i,1);return}}validateEventType_(e){X(this.allowedEvents_.find(a=>a===e),"Unknown event: "+e)}}/**
 * @license
 * Copyright 2025 Google LLC
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
 */class he extends ws{static getInstance(){return new he}constructor(){super(["visible"]);let e,a;typeof document<"u"&&typeof document.addEventListener<"u"&&(typeof document.hidden<"u"?(a="visibilitychange",e="hidden"):typeof document.mozHidden<"u"?(a="mozvisibilitychange",e="mozHidden"):typeof document.msHidden<"u"?(a="msvisibilitychange",e="msHidden"):typeof document.webkitHidden<"u"&&(a="webkitvisibilitychange",e="webkitHidden")),this.visible_=!0,a&&document.addEventListener(a,()=>{const n=!document[e];n!==this.visible_&&(this.visible_=n,this.trigger("visible",n))},!1)}getInitialEvent(e){return X(e==="visible","Unknown event type: "+e),[this.visible_]}}/**
 * @license
 * Copyright 2025 Google LLC
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
 */const Ss="X-Goog-Api-Key",Ts="X-Goog-Firebase-Installations-Auth",Y=8,Fe=3,Ne=-1,Pe=0,Be="featureDisabled",ve="retryIntervalSeconds",$e="latestTemplateVersionNumber";class ys{constructor(e,a,n,s,i,r,o,c,l,f){this.firebaseInstallations=e,this.storage=a,this.sdkVersion=n,this.namespace=s,this.projectId=i,this.apiKey=r,this.appId=o,this.logger=c,this.storageCache=l,this.cachingClient=f,this.observers=new Set,this.isConnectionActive=!1,this.isRealtimeDisabled=!1,this.httpRetriesRemaining=Y,this.isInBackground=!1,this.decoder=new TextDecoder("utf-8"),this.isClosingConnection=!1,this.propagateError=h=>this.observers.forEach(u=>u.error?.(h)),this.isStatusCodeRetryable=h=>!h||[408,429,502,503,504].includes(h),this.setRetriesRemaining(),he.getInstance().on("visible",this.onVisibilityChange,this)}async setRetriesRemaining(){const a=(await this.storage.getRealtimeBackoffMetadata())?.numFailedStreams||0;this.httpRetriesRemaining=Math.max(Y-a,1)}async updateBackoffMetadataWithLastFailedStreamConnectionTime(e){const a=((await this.storage.getRealtimeBackoffMetadata())?.numFailedStreams||0)+1,n=v(a,6e4,2);await this.storage.setRealtimeBackoffMetadata({backoffEndTimeMillis:new Date(e.getTime()+n),numFailedStreams:a})}async updateBackoffMetadataWithRetryInterval(e){const a=Date.now(),n=e*1e3,s=new Date(a+n);await this.storage.setRealtimeBackoffMetadata({backoffEndTimeMillis:s,numFailedStreams:0}),await this.retryHttpConnectionWhenBackoffEnds()}async closeRealtimeHttpConnection(){if(!this.isClosingConnection){this.isClosingConnection=!0;try{this.reader&&await this.reader.cancel()}catch{this.logger.debug("Failed to cancel the reader, connection was lost.")}finally{this.reader=void 0}this.controller&&(await this.controller.abort(),this.controller=void 0),this.isClosingConnection=!1}}async resetRealtimeBackoff(){await this.storage.setRealtimeBackoffMetadata({backoffEndTimeMillis:new Date(-1),numFailedStreams:0})}resetRetryCount(){this.httpRetriesRemaining=Y}async establishRealtimeConnection(e,a,n,s){const i=await this.storage.getActiveConfigEtag(),r=await this.storage.getActiveConfigTemplateVersion(),o={[Ss]:this.apiKey,[Ts]:n,"Content-Type":"application/json",Accept:"application/json","If-None-Match":i||"*","Content-Encoding":"gzip"},c={project:this.projectId,namespace:this.namespace,lastKnownVersionNumber:r,appId:this.appId,sdkVersion:this.sdkVersion,appInstanceId:a};return await fetch(e,{method:"POST",headers:o,body:JSON.stringify(c),signal:s})}getRealtimeUrl(){const a=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfigrealtime.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:streamFetchInvalidations?key=${this.apiKey}`;return new URL(a)}async createRealtimeConnection(){const[e,a]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken(!1)]);this.controller=new AbortController;const n=this.getRealtimeUrl();return await this.establishRealtimeConnection(n,e,a,this.controller.signal)}async retryHttpConnectionWhenBackoffEnds(){let e=await this.storage.getRealtimeBackoffMetadata();e||(e={backoffEndTimeMillis:new Date(Ne),numFailedStreams:Pe});const a=new Date(e.backoffEndTimeMillis).getTime(),n=Date.now(),s=Math.max(0,a-n);await this.makeRealtimeHttpConnection(s)}setIsHttpConnectionRunning(e){this.isConnectionActive=e}checkAndSetHttpConnectionFlagIfNotRunning(){const e=this.canEstablishStreamConnection();return e&&this.setIsHttpConnectionRunning(!0),e}fetchResponseIsUpToDate(e,a){return e.config!=null&&e.templateVersion?e.templateVersion>=a:this.storageCache.getLastFetchStatus()==="success"}parseAndValidateConfigUpdateMessage(e){const a=e.indexOf("{"),n=e.indexOf("}",a);return a<0||n<0||a>=n?"":e.substring(a,n+1)}isEventListenersEmpty(){return this.observers.size===0}getRandomInt(e){return Math.floor(Math.random()*e)}executeAllListenerCallbacks(e){this.observers.forEach(a=>a.next(e))}getChangedParams(e,a){const n=new Set,s=new Set(Object.keys(e||{})),i=new Set(Object.keys(a||{}));for(const r of s)(!i.has(r)||e[r]!==a[r])&&n.add(r);for(const r of i)s.has(r)||n.add(r);return n}async fetchLatestConfig(e,a){const n=e-1,s=Fe-n,i=this.storageCache.getCustomSignals();i&&this.logger.debug(`Fetching config with custom signals: ${JSON.stringify(i)}`);const r=new ns;try{const o={cacheMaxAgeMillis:0,signal:r,customSignals:i,fetchType:"REALTIME",fetchAttempt:s},c=await this.cachingClient.fetch(o);let l=await this.storage.getActiveConfig();if(!this.fetchResponseIsUpToDate(c,a)){this.logger.debug("Fetched template version is the same as SDK's current version. Retrying fetch."),await this.autoFetch(n,a);return}if(c.config==null){this.logger.debug("The fetch succeeded, but the backend had no updates.");return}l==null&&(l={});const f=this.getChangedParams(c.config,l);if(f.size===0){this.logger.debug("Config was fetched, but no params changed.");return}const h={getUpdatedKeys(){return new Set(f)}};this.executeAllListenerCallbacks(h)}catch(o){const c=o instanceof Error?o.message:String(o),l=g.create("update-not-fetched",{originalErrorMessage:`Failed to auto-fetch config update: ${c}`});this.propagateError(l)}}async autoFetch(e,a){if(e===0){const i=g.create("update-not-fetched",{originalErrorMessage:"Unable to fetch the latest version of the template."});this.propagateError(i);return}const s=this.getRandomInt(4)*1e3;await new Promise(i=>setTimeout(i,s)),await this.fetchLatestConfig(e,a)}async handleNotifications(e){let a,n="";for(;;){const{done:s,value:i}=await e.read();if(s)break;if(a=this.decoder.decode(i,{stream:!0}),n+=a,a.includes("}")){if(n=this.parseAndValidateConfigUpdateMessage(n),n.length===0)continue;try{const r=JSON.parse(n);if(this.isEventListenersEmpty())break;if(Be in r&&r[Be]===!0){const o=g.create("realtime-unavailable",{originalErrorMessage:"The server is temporarily unavailable. Try again in a few minutes."});this.propagateError(o);break}if($e in r){const o=await this.storage.getActiveConfigTemplateVersion(),c=Number(r[$e]);o&&c>o&&await this.autoFetch(Fe,c)}if(ve in r){const o=Number(r[ve]);await this.updateBackoffMetadataWithRetryInterval(o)}}catch(r){this.logger.debug("Unable to parse latest config update message.",r);const o=r instanceof Error?r.message:String(r);this.propagateError(g.create("update-message-invalid",{originalErrorMessage:o}))}n=""}}}async listenForNotifications(e){try{await this.handleNotifications(e)}catch{this.isInBackground||this.logger.debug("Real-time connection was closed due to an exception.")}}async prepareAndBeginRealtimeHttpStream(){if(!this.checkAndSetHttpConnectionFlagIfNotRunning())return;let e=await this.storage.getRealtimeBackoffMetadata();e||(e={backoffEndTimeMillis:new Date(Ne),numFailedStreams:Pe});const a=e.backoffEndTimeMillis.getTime();if(Date.now()<a){await this.retryHttpConnectionWhenBackoffEnds();return}let n,s;try{if(n=await this.createRealtimeConnection(),s=n.status,n.ok&&n.body){this.resetRetryCount(),await this.resetRealtimeBackoff();const i=n.body.getReader();this.reader=i,await this.listenForNotifications(i)}}catch(i){this.isInBackground?this.resetRetryCount():this.logger.debug("Exception connecting to real-time RC backend. Retrying the connection...:",i)}finally{await this.closeRealtimeHttpConnection(),this.setIsHttpConnectionRunning(!1);const i=!this.isInBackground&&(s===void 0||this.isStatusCodeRetryable(s));if(i&&await this.updateBackoffMetadataWithLastFailedStreamConnectionTime(new Date),i||n?.ok)await this.retryHttpConnectionWhenBackoffEnds();else{const r=`Unable to connect to the server. HTTP status code: ${s}`,o=g.create("stream-error",{originalErrorMessage:r});this.propagateError(o)}}}canEstablishStreamConnection(){const e=this.observers.size>0,a=!this.isRealtimeDisabled,n=!this.isConnectionActive,s=!this.isInBackground;return e&&a&&n&&s}async makeRealtimeHttpConnection(e){if(this.canEstablishStreamConnection()){if(this.httpRetriesRemaining>0)this.httpRetriesRemaining--,await new Promise(a=>setTimeout(a,e)),this.prepareAndBeginRealtimeHttpStream();else if(!this.isInBackground){const a=g.create("stream-error",{originalErrorMessage:"Unable to connect to the server. Check your connection and try again."});this.propagateError(a)}}}async beginRealtime(){this.observers.size>0&&await this.makeRealtimeHttpConnection(0)}addObserver(e){this.observers.add(e),this.beginRealtime()}removeObserver(e){this.observers.has(e)&&this.observers.delete(e)}async onVisibilityChange(e){this.isInBackground=!e,e?e&&await this.beginRealtime():await this.closeRealtimeHttpConnection()}}/**
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
 */function As(){y(new T(ss,t,"PUBLIC").setMultipleInstances(!0)),C(z,ke),C(z,ke,"esm2020");function t(e,{options:a}){const n=e.getProvider("app").getImmediate(),s=e.getProvider("installations-internal").getImmediate(),{projectId:i,apiKey:r,appId:o}=n.options;if(!i)throw g.create("registration-project-id");if(!r)throw g.create("registration-api-key");if(!o)throw g.create("registration-app-id");const c=a?.templateId||"firebase",l=te()?new _s(o,n.name,c):new Is,f=new bs(l),h=new ae(z);h.logLevel=d.ERROR;const u=new ls(s,Ee,c,i,r,o),_=new us(u,l),I=new os(_,l,f,h),D=new ys(s,l,Ee,c,i,r,o,h,f,I),M=new ms(n,I,f,l,h,D);return rs(M),M}}As();const Ds=t=>Object.fromEntries(new URLSearchParams(t)),Rs=()=>{const t=It(),e=Ds(t.search);return"utm_campaign"in e&&"utm_medium"in e&&"utm_source"in e?{traffic_campaign:e.utm_campaign,traffic_medium:e.utm_medium,traffic_source:e.utm_source}:{}},Fs=()=>{const t=Rs();return{logEvent:_t.useCallback((a,n)=>{},[t])}};var Os=(t=>(t.CLICKED_BOOKING="hasClickedBooking",t.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",t.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",t.CLICKED_CONSULT_CGU="hasClickedConsultCGU",t.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",t.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",t.CLICKED_CREATE_VENUE="hasClickedCreateVenue",t.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",t.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",t.CLICKED_SAVE_VENUE="hasClickedSaveVenue",t.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",t.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",t.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",t.CLICKED_EDIT_PROFILE="hasClickedEditProfile",t.CLICKED_EDIT_COLLECTIVE_OFFER="hasClickedEditCollectiveOffer",t.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",t.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",t.CLICKED_UNKNOWN_SIRET="hasClickedUnknownSiret",t.CLICKED_HELP_CENTER="hasClickedHelpCenter",t.CLICKED_HOME="hasClickedHome",t.CLICKED_LOGOUT="hasClickedLogout",t.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER="hasClickedConfirmedAddHeadlineOffer",t.CLICKED_DISCOVERED_HEADLINE_OFFER="hasClickedDiscoveredHeadlineOffer",t.CLICKED_VIEW_APP_HEADLINE_OFFER="hasClickedViewAppHeadlineOffer",t.CLICKED_OFFER="hasClickedOffer",t.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",t.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",t.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",t.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",t.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",t.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",t.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",t.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",t.CLICKED_PRO="hasClickedPro",t.CLICKED_REIMBURSEMENT="hasClickedReimbursement",t.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",t.CLICKED_STATS="hasClickedOffererStats",t.CLICKED_TICKET="hasClickedTicket",t.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",t.CLICKED_DUPLICATE_BOOKABLE_OFFER="hasClickedDuplicateBookableOffer",t.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",t.CLICKED_HELP_LINK="hasClickedHelpLink",t.CLICKED_RESET_FILTERS="hasClickedResetFilter",t.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",t.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",t.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",t.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",t.CLICKED_CONTACT_OUR_TEAMS="hasClickedContactOurTeams",t.CLICKED_ARCHIVE_COLLECTIVE_OFFER="hasClickedArchiveCollectiveOffer",t.CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER="hasClickedSaveDraftAndExitCollectiveOffer",t.CLICKED_SEE_TEMPLATE_OFFER_EXAMPLE="hasClickedSeeTemplateOfferExample",t.FIRST_LOGIN="firstLogin",t.PAGE_VIEW="page_view",t.SIGNUP_FORM_ABORT="signupFormAbort",t.SIGNUP_FORM_SUCCESS="signupFormSuccess",t.TUTO_PAGE_VIEW="tutoPageView",t.DELETE_DRAFT_OFFER="DeleteDraftOffer",t.CLICKED_NO_VENUE="hasClickedNoVenue",t.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",t.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",t.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",t.CLICKED_ADD_IMAGE="hasClickedAddImage",t.DRAG_OR_SELECTED_IMAGE="hasDragOrSelectedImage",t.CLICKED_SAVE_IMAGE="hasClickedSaveImage",t.CLICKED_DELETE_STOCK="hasClickedDeleteStock",t.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",t.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",t.CLICKED_PAGE_FOR_APP_HOME="hasClickedPageForAppHome",t.CLICKED_PAGE_FOR_ADAGE_HOME="hasClickedPageForAdageHome",t.CLICKED_INVOICES_DOWNLOAD="hasClickedInvoicesDownload",t.CLICKED_PUBLISH_FUTURE_OFFER_EARLIER="hasClickedPublishFutureOfferEarlier",t.EXTRA_PRO_DATA="extra_pro_data",t.CLICKED_NEW_EVOLUTIONS="hasClickedNewEvolutions",t.CLICKED_CONSULT_HELP="hasClickedConsultHelp",t.UPDATED_BOOKING_LIMIT_DATE="hasUpdatedBookingLimitDate",t.CLICKED_GENERATE_TEMPLATE_DESCRIPTION="hasClickedGenerateTemplateDescription",t.UPDATED_EVENT_STOCK_FILTERS="hasUpdatedEventStockFilters",t.CLICKED_VALIDATE_ADD_RECURRENCE_DATES="hasClickedValidateAddRecurrenceDates",t.FAKE_DOOR_VIDEO_INTERESTED="fakeDoorVideoInterested",t.CLICKED_SORT_STOCKS_TABLE="hasClickedSortStocksTable",t.OFFER_FORM_VIDEO_URL_ERROR="videoUrlError",t))(Os||{});export{Os as E,Fs as u};
