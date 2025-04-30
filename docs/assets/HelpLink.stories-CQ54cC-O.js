import{j as P}from"./jsx-runtime-BYYWji4R.js";import{V as pt}from"./index-BQRgOAGl.js";import{r as mt}from"./index-ClcD9ViR.js";import"./config-BdqymTTq.js";import{u as Ct}from"./index-DOYoWpww.js";import{f as _t}from"./full-help-blUMxBcv.js";import{S as Et}from"./SvgIcon-CyWUmZpn.js";import"./_commonjsHelpers-Cpj98o6Y.js";import"./index-J01lmiDr.js";/**
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
 */const Me=function(e){const t=[];let a=0;for(let n=0;n<e.length;n++){let s=e.charCodeAt(n);s<128?t[a++]=s:s<2048?(t[a++]=s>>6|192,t[a++]=s&63|128):(s&64512)===55296&&n+1<e.length&&(e.charCodeAt(n+1)&64512)===56320?(s=65536+((s&1023)<<10)+(e.charCodeAt(++n)&1023),t[a++]=s>>18|240,t[a++]=s>>12&63|128,t[a++]=s>>6&63|128,t[a++]=s&63|128):(t[a++]=s>>12|224,t[a++]=s>>6&63|128,t[a++]=s&63|128)}return t},It=function(e){const t=[];let a=0,n=0;for(;a<e.length;){const s=e[a++];if(s<128)t[n++]=String.fromCharCode(s);else if(s>191&&s<224){const r=e[a++];t[n++]=String.fromCharCode((s&31)<<6|r&63)}else if(s>239&&s<365){const r=e[a++],i=e[a++],o=e[a++],c=((s&7)<<18|(r&63)<<12|(i&63)<<6|o&63)-65536;t[n++]=String.fromCharCode(55296+(c>>10)),t[n++]=String.fromCharCode(56320+(c&1023))}else{const r=e[a++],i=e[a++];t[n++]=String.fromCharCode((s&15)<<12|(r&63)<<6|i&63)}}return t.join("")},bt={byteToCharMap_:null,charToByteMap_:null,byteToCharMapWebSafe_:null,charToByteMapWebSafe_:null,ENCODED_VALS_BASE:"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",get ENCODED_VALS(){return this.ENCODED_VALS_BASE+"+/="},get ENCODED_VALS_WEBSAFE(){return this.ENCODED_VALS_BASE+"-_."},HAS_NATIVE_SUPPORT:typeof atob=="function",encodeByteArray(e,t){if(!Array.isArray(e))throw Error("encodeByteArray takes an array as a parameter");this.init_();const a=t?this.byteToCharMapWebSafe_:this.byteToCharMap_,n=[];for(let s=0;s<e.length;s+=3){const r=e[s],i=s+1<e.length,o=i?e[s+1]:0,c=s+2<e.length,l=c?e[s+2]:0,h=r>>2,d=(r&3)<<4|o>>4;let f=(o&15)<<2|l>>6,g=l&63;c||(g=64,i||(f=64)),n.push(a[h],a[d],a[f],a[g])}return n.join("")},encodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?btoa(e):this.encodeByteArray(Me(e),t)},decodeString(e,t){return this.HAS_NATIVE_SUPPORT&&!t?atob(e):It(this.decodeStringToByteArray(e,t))},decodeStringToByteArray(e,t){this.init_();const a=t?this.charToByteMapWebSafe_:this.charToByteMap_,n=[];for(let s=0;s<e.length;){const r=a[e.charAt(s++)],o=s<e.length?a[e.charAt(s)]:0;++s;const l=s<e.length?a[e.charAt(s)]:64;++s;const d=s<e.length?a[e.charAt(s)]:64;if(++s,r==null||o==null||l==null||d==null)throw new St;const f=r<<2|o>>4;if(n.push(f),l!==64){const g=o<<4&240|l>>2;if(n.push(g),d!==64){const O=l<<6&192|d;n.push(O)}}}return n},init_(){if(!this.byteToCharMap_){this.byteToCharMap_={},this.charToByteMap_={},this.byteToCharMapWebSafe_={},this.charToByteMapWebSafe_={};for(let e=0;e<this.ENCODED_VALS.length;e++)this.byteToCharMap_[e]=this.ENCODED_VALS.charAt(e),this.charToByteMap_[this.byteToCharMap_[e]]=e,this.byteToCharMapWebSafe_[e]=this.ENCODED_VALS_WEBSAFE.charAt(e),this.charToByteMapWebSafe_[this.byteToCharMapWebSafe_[e]]=e,e>=this.ENCODED_VALS_BASE.length&&(this.charToByteMap_[this.ENCODED_VALS_WEBSAFE.charAt(e)]=e,this.charToByteMapWebSafe_[this.ENCODED_VALS.charAt(e)]=e)}}};class St extends Error{constructor(){super(...arguments),this.name="DecodeBase64StringError"}}const wt=function(e){const t=Me(e);return bt.encodeByteArray(t,!0)},Ne=function(e){return wt(e).replace(/\./g,"")};function Tt(){const e=typeof chrome=="object"?chrome.runtime:typeof browser=="object"?browser.runtime:void 0;return typeof e=="object"&&e.id!==void 0}function ee(){try{return typeof indexedDB=="object"}catch{return!1}}function ve(){return new Promise((e,t)=>{try{let a=!0;const n="validate-browser-context-for-indexeddb-analytics-module",s=self.indexedDB.open(n);s.onsuccess=()=>{s.result.close(),a||self.indexedDB.deleteDatabase(n),e(!0)},s.onupgradeneeded=()=>{a=!1},s.onerror=()=>{var r;t(((r=s.error)===null||r===void 0?void 0:r.message)||"")}}catch(a){t(a)}})}function yt(){return!(typeof navigator>"u"||!navigator.cookieEnabled)}/**
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
 */const At="FirebaseError";class D extends Error{constructor(t,a,n){super(a),this.code=t,this.customData=n,this.name=At,Object.setPrototypeOf(this,D.prototype),Error.captureStackTrace&&Error.captureStackTrace(this,N.prototype.create)}}class N{constructor(t,a,n){this.service=t,this.serviceName=a,this.errors=n}create(t,...a){const n=a[0]||{},s=`${this.service}/${t}`,r=this.errors[t],i=r?Dt(r,n):"Error",o=`${this.serviceName}: ${i} (${s}).`;return new D(s,o,n)}}function Dt(e,t){return e.replace(Ot,(a,n)=>{const s=t[n];return s!=null?String(s):`<${n}?>`})}const Ot=/\{\$([^}]+)}/g;/**
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
 */const Lt=1e3,Rt=2,Ft=4*60*60*1e3,Pt=.5;function Y(e,t=Lt,a=Rt){const n=t*Math.pow(a,e),s=Math.round(Pt*n*(Math.random()-.5)*2);return Math.min(Ft,n+s)}/**
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
 */function Be(e){return e&&e._delegate?e._delegate:e}class y{constructor(t,a,n){this.name=t,this.instanceFactory=a,this.type=n,this.multipleInstances=!1,this.serviceProps={},this.instantiationMode="LAZY",this.onInstanceCreated=null}setInstantiationMode(t){return this.instantiationMode=t,this}setMultipleInstances(t){return this.multipleInstances=t,this}setServiceProps(t){return this.serviceProps=t,this}setInstanceCreatedCallback(t){return this.onInstanceCreated=t,this}}/**
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
 */var u;(function(e){e[e.DEBUG=0]="DEBUG",e[e.VERBOSE=1]="VERBOSE",e[e.INFO=2]="INFO",e[e.WARN=3]="WARN",e[e.ERROR=4]="ERROR",e[e.SILENT=5]="SILENT"})(u||(u={}));const kt={debug:u.DEBUG,verbose:u.VERBOSE,info:u.INFO,warn:u.WARN,error:u.ERROR,silent:u.SILENT},Mt=u.INFO,Nt={[u.DEBUG]:"log",[u.VERBOSE]:"log",[u.INFO]:"info",[u.WARN]:"warn",[u.ERROR]:"error"},vt=(e,t,...a)=>{if(t<e.logLevel)return;const n=new Date().toISOString(),s=Nt[t];if(s)console[s](`[${n}]  ${e.name}:`,...a);else throw new Error(`Attempted to log a message with an invalid logType (value: ${t})`)};class te{constructor(t){this.name=t,this._logLevel=Mt,this._logHandler=vt,this._userLogHandler=null}get logLevel(){return this._logLevel}set logLevel(t){if(!(t in u))throw new TypeError(`Invalid value "${t}" assigned to \`logLevel\``);this._logLevel=t}setLogLevel(t){this._logLevel=typeof t=="string"?kt[t]:t}get logHandler(){return this._logHandler}set logHandler(t){if(typeof t!="function")throw new TypeError("Value assigned to `logHandler` must be a function");this._logHandler=t}get userLogHandler(){return this._userLogHandler}set userLogHandler(t){this._userLogHandler=t}debug(...t){this._userLogHandler&&this._userLogHandler(this,u.DEBUG,...t),this._logHandler(this,u.DEBUG,...t)}log(...t){this._userLogHandler&&this._userLogHandler(this,u.VERBOSE,...t),this._logHandler(this,u.VERBOSE,...t)}info(...t){this._userLogHandler&&this._userLogHandler(this,u.INFO,...t),this._logHandler(this,u.INFO,...t)}warn(...t){this._userLogHandler&&this._userLogHandler(this,u.WARN,...t),this._logHandler(this,u.WARN,...t)}error(...t){this._userLogHandler&&this._userLogHandler(this,u.ERROR,...t),this._logHandler(this,u.ERROR,...t)}}const Bt=(e,t)=>t.some(a=>e instanceof a);let ue,de;function $t(){return ue||(ue=[IDBDatabase,IDBObjectStore,IDBIndex,IDBCursor,IDBTransaction])}function Kt(){return de||(de=[IDBCursor.prototype.advance,IDBCursor.prototype.continue,IDBCursor.prototype.continuePrimaryKey])}const $e=new WeakMap,X=new WeakMap,Ke=new WeakMap,x=new WeakMap,ae=new WeakMap;function Ht(e){const t=new Promise((a,n)=>{const s=()=>{e.removeEventListener("success",r),e.removeEventListener("error",i)},r=()=>{a(T(e.result)),s()},i=()=>{n(e.error),s()};e.addEventListener("success",r),e.addEventListener("error",i)});return t.then(a=>{a instanceof IDBCursor&&$e.set(a,e)}).catch(()=>{}),ae.set(t,e),t}function xt(e){if(X.has(e))return;const t=new Promise((a,n)=>{const s=()=>{e.removeEventListener("complete",r),e.removeEventListener("error",i),e.removeEventListener("abort",i)},r=()=>{a(),s()},i=()=>{n(e.error||new DOMException("AbortError","AbortError")),s()};e.addEventListener("complete",r),e.addEventListener("error",i),e.addEventListener("abort",i)});X.set(e,t)}let J={get(e,t,a){if(e instanceof IDBTransaction){if(t==="done")return X.get(e);if(t==="objectStoreNames")return e.objectStoreNames||Ke.get(e);if(t==="store")return a.objectStoreNames[1]?void 0:a.objectStore(a.objectStoreNames[0])}return T(e[t])},set(e,t,a){return e[t]=a,!0},has(e,t){return e instanceof IDBTransaction&&(t==="done"||t==="store")?!0:t in e}};function Vt(e){J=e(J)}function Ut(e){return e===IDBDatabase.prototype.transaction&&!("objectStoreNames"in IDBTransaction.prototype)?function(t,...a){const n=e.call(V(this),t,...a);return Ke.set(n,t.sort?t.sort():[t]),T(n)}:Kt().includes(e)?function(...t){return e.apply(V(this),t),T($e.get(this))}:function(...t){return T(e.apply(V(this),t))}}function jt(e){return typeof e=="function"?Ut(e):(e instanceof IDBTransaction&&xt(e),Bt(e,$t())?new Proxy(e,J):e)}function T(e){if(e instanceof IDBRequest)return Ht(e);if(x.has(e))return x.get(e);const t=jt(e);return t!==e&&(x.set(e,t),ae.set(t,e)),t}const V=e=>ae.get(e);function He(e,t,{blocked:a,upgrade:n,blocking:s,terminated:r}={}){const i=indexedDB.open(e,t),o=T(i);return n&&i.addEventListener("upgradeneeded",c=>{n(T(i.result),c.oldVersion,c.newVersion,T(i.transaction),c)}),a&&i.addEventListener("blocked",c=>a(c.oldVersion,c.newVersion,c)),o.then(c=>{r&&c.addEventListener("close",()=>r()),s&&c.addEventListener("versionchange",l=>s(l.oldVersion,l.newVersion,l))}).catch(()=>{}),o}const Gt=["get","getKey","getAll","getAllKeys","count"],Wt=["put","add","delete","clear"],U=new Map;function he(e,t){if(!(e instanceof IDBDatabase&&!(t in e)&&typeof t=="string"))return;if(U.get(t))return U.get(t);const a=t.replace(/FromIndex$/,""),n=t!==a,s=Wt.includes(a);if(!(a in(n?IDBIndex:IDBObjectStore).prototype)||!(s||Gt.includes(a)))return;const r=async function(i,...o){const c=this.transaction(i,s?"readwrite":"readonly");let l=c.store;return n&&(l=l.index(o.shift())),(await Promise.all([l[a](...o),s&&c.done]))[0]};return U.set(t,r),r}Vt(e=>({...e,get:(t,a,n)=>he(t,a)||e.get(t,a,n),has:(t,a)=>!!he(t,a)||e.has(t,a)}));/**
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
 */class qt{constructor(t){this.container=t}getPlatformInfoString(){return this.container.getProviders().map(a=>{if(zt(a)){const n=a.getImmediate();return`${n.library}/${n.version}`}else return null}).filter(a=>a).join(" ")}}function zt(e){const t=e.getComponent();return(t==null?void 0:t.type)==="VERSION"}const Q="@firebase/app",fe="0.11.5";/**
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
 */const I=new te("@firebase/app"),Yt="@firebase/app-compat",Xt="@firebase/analytics-compat",Jt="@firebase/analytics",Qt="@firebase/app-check-compat",Zt="@firebase/app-check",ea="@firebase/auth",ta="@firebase/auth-compat",aa="@firebase/database",na="@firebase/data-connect",sa="@firebase/database-compat",ra="@firebase/functions",ia="@firebase/functions-compat",oa="@firebase/installations",ca="@firebase/installations-compat",la="@firebase/messaging",ua="@firebase/messaging-compat",da="@firebase/performance",ha="@firebase/performance-compat",fa="@firebase/remote-config",ga="@firebase/remote-config-compat",pa="@firebase/storage",ma="@firebase/storage-compat",Ca="@firebase/firestore",_a="@firebase/vertexai",Ea="@firebase/firestore-compat",Ia="firebase",ba="11.6.1",Sa={[Q]:"fire-core",[Yt]:"fire-core-compat",[Jt]:"fire-analytics",[Xt]:"fire-analytics-compat",[Zt]:"fire-app-check",[Qt]:"fire-app-check-compat",[ea]:"fire-auth",[ta]:"fire-auth-compat",[aa]:"fire-rtdb",[na]:"fire-data-connect",[sa]:"fire-rtdb-compat",[ra]:"fire-fn",[ia]:"fire-fn-compat",[oa]:"fire-iid",[ca]:"fire-iid-compat",[la]:"fire-fcm",[ua]:"fire-fcm-compat",[da]:"fire-perf",[ha]:"fire-perf-compat",[fa]:"fire-rc",[ga]:"fire-rc-compat",[pa]:"fire-gcs",[ma]:"fire-gcs-compat",[Ca]:"fire-fst",[Ea]:"fire-fst-compat",[_a]:"fire-vertex","fire-js":"fire-js",[Ia]:"fire-js-all"};/**
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
 */const wa=new Map,Ta=new Map,ge=new Map;function pe(e,t){try{e.container.addComponent(t)}catch(a){I.debug(`Component ${t.name} failed to register with FirebaseApp ${e.name}`,a)}}function A(e){const t=e.name;if(ge.has(t))return I.debug(`There were multiple attempts to register component ${t}.`),!1;ge.set(t,e);for(const a of wa.values())pe(a,e);for(const a of Ta.values())pe(a,e);return!0}function xe(e,t){const a=e.container.getProvider("heartbeat").getImmediate({optional:!0});return a&&a.triggerHeartbeat(),e.container.getProvider(t)}/**
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
 */const ya={"no-app":"No Firebase App '{$appName}' has been created - call initializeApp() first","bad-app-name":"Illegal App name: '{$appName}'","duplicate-app":"Firebase App named '{$appName}' already exists with different options or config","app-deleted":"Firebase App named '{$appName}' already deleted","server-app-deleted":"Firebase Server App has been deleted","no-options":"Need to provide options, when not being deployed to hosting via source.","invalid-app-argument":"firebase.{$appName}() takes either no argument or a Firebase App instance.","invalid-log-argument":"First argument to `onLog` must be null or a function.","idb-open":"Error thrown when opening IndexedDB. Original error: {$originalErrorMessage}.","idb-get":"Error thrown when reading from IndexedDB. Original error: {$originalErrorMessage}.","idb-set":"Error thrown when writing to IndexedDB. Original error: {$originalErrorMessage}.","idb-delete":"Error thrown when deleting from IndexedDB. Original error: {$originalErrorMessage}.","finalization-registry-not-supported":"FirebaseServerApp deleteOnDeref field defined but the JS runtime does not support FinalizationRegistry.","invalid-server-app-environment":"FirebaseServerApp is not for use in browser environments."},ne=new N("app","Firebase",ya);/**
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
 */const Aa=ba;function E(e,t,a){var n;let s=(n=Sa[e])!==null&&n!==void 0?n:e;a&&(s+=`-${a}`);const r=s.match(/\s|\//),i=t.match(/\s|\//);if(r||i){const o=[`Unable to register library "${s}" with version "${t}":`];r&&o.push(`library name "${s}" contains illegal characters (whitespace or "/")`),r&&i&&o.push("and"),i&&o.push(`version name "${t}" contains illegal characters (whitespace or "/")`),I.warn(o.join(" "));return}A(new y(`${s}-version`,()=>({library:s,version:t}),"VERSION"))}/**
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
 */const Da="firebase-heartbeat-database",Oa=1,M="firebase-heartbeat-store";let j=null;function Ve(){return j||(j=He(Da,Oa,{upgrade:(e,t)=>{switch(t){case 0:try{e.createObjectStore(M)}catch(a){console.warn(a)}}}}).catch(e=>{throw ne.create("idb-open",{originalErrorMessage:e.message})})),j}async function La(e){try{const a=(await Ve()).transaction(M),n=await a.objectStore(M).get(Ue(e));return await a.done,n}catch(t){if(t instanceof D)I.warn(t.message);else{const a=ne.create("idb-get",{originalErrorMessage:t==null?void 0:t.message});I.warn(a.message)}}}async function me(e,t){try{const n=(await Ve()).transaction(M,"readwrite");await n.objectStore(M).put(t,Ue(e)),await n.done}catch(a){if(a instanceof D)I.warn(a.message);else{const n=ne.create("idb-set",{originalErrorMessage:a==null?void 0:a.message});I.warn(n.message)}}}function Ue(e){return`${e.name}!${e.options.appId}`}/**
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
 */const Ra=1024,Fa=30;class Pa{constructor(t){this.container=t,this._heartbeatsCache=null;const a=this.container.getProvider("app").getImmediate();this._storage=new Ma(a),this._heartbeatsCachePromise=this._storage.read().then(n=>(this._heartbeatsCache=n,n))}async triggerHeartbeat(){var t,a;try{const s=this.container.getProvider("platform-logger").getImmediate().getPlatformInfoString(),r=Ce();if(((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null&&(this._heartbeatsCache=await this._heartbeatsCachePromise,((a=this._heartbeatsCache)===null||a===void 0?void 0:a.heartbeats)==null)||this._heartbeatsCache.lastSentHeartbeatDate===r||this._heartbeatsCache.heartbeats.some(i=>i.date===r))return;if(this._heartbeatsCache.heartbeats.push({date:r,agent:s}),this._heartbeatsCache.heartbeats.length>Fa){const i=Na(this._heartbeatsCache.heartbeats);this._heartbeatsCache.heartbeats.splice(i,1)}return this._storage.overwrite(this._heartbeatsCache)}catch(n){I.warn(n)}}async getHeartbeatsHeader(){var t;try{if(this._heartbeatsCache===null&&await this._heartbeatsCachePromise,((t=this._heartbeatsCache)===null||t===void 0?void 0:t.heartbeats)==null||this._heartbeatsCache.heartbeats.length===0)return"";const a=Ce(),{heartbeatsToSend:n,unsentEntries:s}=ka(this._heartbeatsCache.heartbeats),r=Ne(JSON.stringify({version:2,heartbeats:n}));return this._heartbeatsCache.lastSentHeartbeatDate=a,s.length>0?(this._heartbeatsCache.heartbeats=s,await this._storage.overwrite(this._heartbeatsCache)):(this._heartbeatsCache.heartbeats=[],this._storage.overwrite(this._heartbeatsCache)),r}catch(a){return I.warn(a),""}}}function Ce(){return new Date().toISOString().substring(0,10)}function ka(e,t=Ra){const a=[];let n=e.slice();for(const s of e){const r=a.find(i=>i.agent===s.agent);if(r){if(r.dates.push(s.date),_e(a)>t){r.dates.pop();break}}else if(a.push({agent:s.agent,dates:[s.date]}),_e(a)>t){a.pop();break}n=n.slice(1)}return{heartbeatsToSend:a,unsentEntries:n}}class Ma{constructor(t){this.app=t,this._canUseIndexedDBPromise=this.runIndexedDBEnvironmentCheck()}async runIndexedDBEnvironmentCheck(){return ee()?ve().then(()=>!0).catch(()=>!1):!1}async read(){if(await this._canUseIndexedDBPromise){const a=await La(this.app);return a!=null&&a.heartbeats?a:{heartbeats:[]}}else return{heartbeats:[]}}async overwrite(t){var a;if(await this._canUseIndexedDBPromise){const s=await this.read();return me(this.app,{lastSentHeartbeatDate:(a=t.lastSentHeartbeatDate)!==null&&a!==void 0?a:s.lastSentHeartbeatDate,heartbeats:t.heartbeats})}else return}async add(t){var a;if(await this._canUseIndexedDBPromise){const s=await this.read();return me(this.app,{lastSentHeartbeatDate:(a=t.lastSentHeartbeatDate)!==null&&a!==void 0?a:s.lastSentHeartbeatDate,heartbeats:[...s.heartbeats,...t.heartbeats]})}else return}}function _e(e){return Ne(JSON.stringify({version:2,heartbeats:e})).length}function Na(e){if(e.length===0)return-1;let t=0,a=e[0].date;for(let n=1;n<e.length;n++)e[n].date<a&&(a=e[n].date,t=n);return t}/**
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
 */function va(e){A(new y("platform-logger",t=>new qt(t),"PRIVATE")),A(new y("heartbeat",t=>new Pa(t),"PRIVATE")),E(Q,fe,e),E(Q,fe,"esm2017"),E("fire-js","")}va("");const je="@firebase/installations",se="0.6.13";/**
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
 */const Ge=1e4,We=`w:${se}`,qe="FIS_v2",Ba="https://firebaseinstallations.googleapis.com/v1",$a=60*60*1e3,Ka="installations",Ha="Installations";/**
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
 */const xa={"missing-app-config-values":'Missing App configuration value: "{$valueName}"',"not-registered":"Firebase Installation is not registered.","installation-not-found":"Firebase Installation not found.","request-failed":'{$requestName} request failed with error "{$serverCode} {$serverStatus}: {$serverMessage}"',"app-offline":"Could not process request. Application offline.","delete-pending-registration":"Can't delete installation while there is a pending registration request."},R=new N(Ka,Ha,xa);function ze(e){return e instanceof D&&e.code.includes("request-failed")}/**
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
 */function Ye({projectId:e}){return`${Ba}/projects/${e}/installations`}function Xe(e){return{token:e.token,requestStatus:2,expiresIn:Ua(e.expiresIn),creationTime:Date.now()}}async function Je(e,t){const n=(await t.json()).error;return R.create("request-failed",{requestName:e,serverCode:n.code,serverMessage:n.message,serverStatus:n.status})}function Qe({apiKey:e}){return new Headers({"Content-Type":"application/json",Accept:"application/json","x-goog-api-key":e})}function Va(e,{refreshToken:t}){const a=Qe(e);return a.append("Authorization",ja(t)),a}async function Ze(e){const t=await e();return t.status>=500&&t.status<600?e():t}function Ua(e){return Number(e.replace("s","000"))}function ja(e){return`${qe} ${e}`}/**
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
 */async function Ga({appConfig:e,heartbeatServiceProvider:t},{fid:a}){const n=Ye(e),s=Qe(e),r=t.getImmediate({optional:!0});if(r){const l=await r.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={fid:a,authVersion:qe,appId:e.appId,sdkVersion:We},o={method:"POST",headers:s,body:JSON.stringify(i)},c=await Ze(()=>fetch(n,o));if(c.ok){const l=await c.json();return{fid:l.fid||a,registrationStatus:2,refreshToken:l.refreshToken,authToken:Xe(l.authToken)}}else throw await Je("Create Installation",c)}/**
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
 */function et(e){return new Promise(t=>{setTimeout(t,e)})}/**
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
 */function Wa(e){return btoa(String.fromCharCode(...e)).replace(/\+/g,"-").replace(/\//g,"_")}/**
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
 */const qa=/^[cdef][\w-]{21}$/,Z="";function za(){try{const e=new Uint8Array(17);(self.crypto||self.msCrypto).getRandomValues(e),e[0]=112+e[0]%16;const a=Ya(e);return qa.test(a)?a:Z}catch{return Z}}function Ya(e){return Wa(e).substr(0,22)}/**
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
 */function K(e){return`${e.appName}!${e.appId}`}/**
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
 */const tt=new Map;function at(e,t){const a=K(e);nt(a,t),Xa(a,t)}function nt(e,t){const a=tt.get(e);if(a)for(const n of a)n(t)}function Xa(e,t){const a=Ja();a&&a.postMessage({key:e,fid:t}),Qa()}let L=null;function Ja(){return!L&&"BroadcastChannel"in self&&(L=new BroadcastChannel("[Firebase] FID Change"),L.onmessage=e=>{nt(e.data.key,e.data.fid)}),L}function Qa(){tt.size===0&&L&&(L.close(),L=null)}/**
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
 */const Za="firebase-installations-database",en=1,F="firebase-installations-store";let G=null;function re(){return G||(G=He(Za,en,{upgrade:(e,t)=>{switch(t){case 0:e.createObjectStore(F)}}})),G}async function $(e,t){const a=K(e),s=(await re()).transaction(F,"readwrite"),r=s.objectStore(F),i=await r.get(a);return await r.put(t,a),await s.done,(!i||i.fid!==t.fid)&&at(e,t.fid),t}async function st(e){const t=K(e),n=(await re()).transaction(F,"readwrite");await n.objectStore(F).delete(t),await n.done}async function H(e,t){const a=K(e),s=(await re()).transaction(F,"readwrite"),r=s.objectStore(F),i=await r.get(a),o=t(i);return o===void 0?await r.delete(a):await r.put(o,a),await s.done,o&&(!i||i.fid!==o.fid)&&at(e,o.fid),o}/**
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
 */async function ie(e){let t;const a=await H(e.appConfig,n=>{const s=tn(n),r=an(e,s);return t=r.registrationPromise,r.installationEntry});return a.fid===Z?{installationEntry:await t}:{installationEntry:a,registrationPromise:t}}function tn(e){const t=e||{fid:za(),registrationStatus:0};return rt(t)}function an(e,t){if(t.registrationStatus===0){if(!navigator.onLine){const s=Promise.reject(R.create("app-offline"));return{installationEntry:t,registrationPromise:s}}const a={fid:t.fid,registrationStatus:1,registrationTime:Date.now()},n=nn(e,a);return{installationEntry:a,registrationPromise:n}}else return t.registrationStatus===1?{installationEntry:t,registrationPromise:sn(e)}:{installationEntry:t}}async function nn(e,t){try{const a=await Ga(e,t);return $(e.appConfig,a)}catch(a){throw ze(a)&&a.customData.serverCode===409?await st(e.appConfig):await $(e.appConfig,{fid:t.fid,registrationStatus:0}),a}}async function sn(e){let t=await Ee(e.appConfig);for(;t.registrationStatus===1;)await et(100),t=await Ee(e.appConfig);if(t.registrationStatus===0){const{installationEntry:a,registrationPromise:n}=await ie(e);return n||a}return t}function Ee(e){return H(e,t=>{if(!t)throw R.create("installation-not-found");return rt(t)})}function rt(e){return rn(e)?{fid:e.fid,registrationStatus:0}:e}function rn(e){return e.registrationStatus===1&&e.registrationTime+Ge<Date.now()}/**
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
 */async function on({appConfig:e,heartbeatServiceProvider:t},a){const n=cn(e,a),s=Va(e,a),r=t.getImmediate({optional:!0});if(r){const l=await r.getHeartbeatsHeader();l&&s.append("x-firebase-client",l)}const i={installation:{sdkVersion:We,appId:e.appId}},o={method:"POST",headers:s,body:JSON.stringify(i)},c=await Ze(()=>fetch(n,o));if(c.ok){const l=await c.json();return Xe(l)}else throw await Je("Generate Auth Token",c)}function cn(e,{fid:t}){return`${Ye(e)}/${t}/authTokens:generate`}/**
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
 */async function oe(e,t=!1){let a;const n=await H(e.appConfig,r=>{if(!it(r))throw R.create("not-registered");const i=r.authToken;if(!t&&dn(i))return r;if(i.requestStatus===1)return a=ln(e,t),r;{if(!navigator.onLine)throw R.create("app-offline");const o=fn(r);return a=un(e,o),o}});return a?await a:n.authToken}async function ln(e,t){let a=await Ie(e.appConfig);for(;a.authToken.requestStatus===1;)await et(100),a=await Ie(e.appConfig);const n=a.authToken;return n.requestStatus===0?oe(e,t):n}function Ie(e){return H(e,t=>{if(!it(t))throw R.create("not-registered");const a=t.authToken;return gn(a)?Object.assign(Object.assign({},t),{authToken:{requestStatus:0}}):t})}async function un(e,t){try{const a=await on(e,t),n=Object.assign(Object.assign({},t),{authToken:a});return await $(e.appConfig,n),a}catch(a){if(ze(a)&&(a.customData.serverCode===401||a.customData.serverCode===404))await st(e.appConfig);else{const n=Object.assign(Object.assign({},t),{authToken:{requestStatus:0}});await $(e.appConfig,n)}throw a}}function it(e){return e!==void 0&&e.registrationStatus===2}function dn(e){return e.requestStatus===2&&!hn(e)}function hn(e){const t=Date.now();return t<e.creationTime||e.creationTime+e.expiresIn<t+$a}function fn(e){const t={requestStatus:1,requestTime:Date.now()};return Object.assign(Object.assign({},e),{authToken:t})}function gn(e){return e.requestStatus===1&&e.requestTime+Ge<Date.now()}/**
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
 */async function pn(e){const t=e,{installationEntry:a,registrationPromise:n}=await ie(t);return n?n.catch(console.error):oe(t).catch(console.error),a.fid}/**
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
 */async function mn(e,t=!1){const a=e;return await Cn(a),(await oe(a,t)).token}async function Cn(e){const{registrationPromise:t}=await ie(e);t&&await t}/**
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
 */function _n(e){if(!e||!e.options)throw W("App Configuration");if(!e.name)throw W("App Name");const t=["projectId","apiKey","appId"];for(const a of t)if(!e.options[a])throw W(a);return{appName:e.name,projectId:e.options.projectId,apiKey:e.options.apiKey,appId:e.options.appId}}function W(e){return R.create("missing-app-config-values",{valueName:e})}/**
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
 */const ot="installations",En="installations-internal",In=e=>{const t=e.getProvider("app").getImmediate(),a=_n(t),n=xe(t,"heartbeat");return{app:t,appConfig:a,heartbeatServiceProvider:n,_delete:()=>Promise.resolve()}},bn=e=>{const t=e.getProvider("app").getImmediate(),a=xe(t,ot).getImmediate();return{getId:()=>pn(a),getToken:s=>mn(a,s)}};function Sn(){A(new y(ot,In,"PUBLIC")),A(new y(En,bn,"PRIVATE"))}Sn();E(je,se);E(je,se,"esm2017");/**
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
 */const be="analytics",wn="firebase_id",Tn="origin",yn=60*1e3,An="https://firebase.googleapis.com/v1alpha/projects/-/apps/{app-id}/webConfig",ce="https://www.googletagmanager.com/gtag/js";/**
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
 */const p=new te("@firebase/analytics");/**
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
 */const Dn={"already-exists":"A Firebase Analytics instance with the appId {$id}  already exists. Only one Firebase Analytics instance can be created for each appId.","already-initialized":"initializeAnalytics() cannot be called again with different options than those it was initially called with. It can be called again with the same options to return the existing instance, or getAnalytics() can be used to get a reference to the already-initialized instance.","already-initialized-settings":"Firebase Analytics has already been initialized.settings() must be called before initializing any Analytics instanceor it will have no effect.","interop-component-reg-failed":"Firebase Analytics Interop Component failed to instantiate: {$reason}","invalid-analytics-context":"Firebase Analytics is not supported in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","indexeddb-unavailable":"IndexedDB unavailable or restricted in this environment. Wrap initialization of analytics in analytics.isSupported() to prevent initialization in unsupported environments. Details: {$errorInfo}","fetch-throttle":"The config fetch request timed out while in an exponential backoff state. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.","config-fetch-failed":"Dynamic config fetch failed: [{$httpStatus}] {$responseMessage}","no-api-key":'The "apiKey" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid API key.',"no-app-id":'The "appId" field is empty in the local Firebase config. Firebase Analytics requires this field tocontain a valid app ID.',"no-client-id":'The "client_id" field is empty.',"invalid-gtag-resource":"Trusted Types detected an invalid gtag resource: {$gtagURL}."},C=new N("analytics","Analytics",Dn);/**
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
 */function On(e){if(!e.startsWith(ce)){const t=C.create("invalid-gtag-resource",{gtagURL:e});return p.warn(t.message),""}return e}function ct(e){return Promise.all(e.map(t=>t.catch(a=>a)))}function Ln(e,t){let a;return window.trustedTypes&&(a=window.trustedTypes.createPolicy(e,t)),a}function Rn(e,t){const a=Ln("firebase-js-sdk-policy",{createScriptURL:On}),n=document.createElement("script"),s=`${ce}?l=${e}&id=${t}`;n.src=a?a==null?void 0:a.createScriptURL(s):s,n.async=!0,document.head.appendChild(n)}function Fn(e){let t=[];return Array.isArray(window[e])?t=window[e]:window[e]=t,t}async function Pn(e,t,a,n,s,r){const i=n[s];try{if(i)await t[i];else{const c=(await ct(a)).find(l=>l.measurementId===s);c&&await t[c.appId]}}catch(o){p.error(o)}e("config",s,r)}async function kn(e,t,a,n,s){try{let r=[];if(s&&s.send_to){let i=s.send_to;Array.isArray(i)||(i=[i]);const o=await ct(a);for(const c of i){const l=o.find(d=>d.measurementId===c),h=l&&t[l.appId];if(h)r.push(h);else{r=[];break}}}r.length===0&&(r=Object.values(t)),await Promise.all(r),e("event",n,s||{})}catch(r){p.error(r)}}function Mn(e,t,a,n){async function s(r,...i){try{if(r==="event"){const[o,c]=i;await kn(e,t,a,o,c)}else if(r==="config"){const[o,c]=i;await Pn(e,t,a,n,o,c)}else if(r==="consent"){const[o,c]=i;e("consent",o,c)}else if(r==="get"){const[o,c,l]=i;e("get",o,c,l)}else if(r==="set"){const[o]=i;e("set",o)}else e(r,...i)}catch(o){p.error(o)}}return s}function Nn(e,t,a,n,s){let r=function(...i){window[n].push(arguments)};return window[s]&&typeof window[s]=="function"&&(r=window[s]),window[s]=Mn(r,e,t,a),{gtagCore:r,wrappedGtag:window[s]}}function vn(e){const t=window.document.getElementsByTagName("script");for(const a of Object.values(t))if(a.src&&a.src.includes(ce)&&a.src.includes(e))return a;return null}/**
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
 */const Bn=30,$n=1e3;class Kn{constructor(t={},a=$n){this.throttleMetadata=t,this.intervalMillis=a}getThrottleMetadata(t){return this.throttleMetadata[t]}setThrottleMetadata(t,a){this.throttleMetadata[t]=a}deleteThrottleMetadata(t){delete this.throttleMetadata[t]}}const lt=new Kn;function Hn(e){return new Headers({Accept:"application/json","x-goog-api-key":e})}async function xn(e){var t;const{appId:a,apiKey:n}=e,s={method:"GET",headers:Hn(n)},r=An.replace("{app-id}",a),i=await fetch(r,s);if(i.status!==200&&i.status!==304){let o="";try{const c=await i.json();!((t=c.error)===null||t===void 0)&&t.message&&(o=c.error.message)}catch{}throw C.create("config-fetch-failed",{httpStatus:i.status,responseMessage:o})}return i.json()}async function Vn(e,t=lt,a){const{appId:n,apiKey:s,measurementId:r}=e.options;if(!n)throw C.create("no-app-id");if(!s){if(r)return{measurementId:r,appId:n};throw C.create("no-api-key")}const i=t.getThrottleMetadata(n)||{backoffCount:0,throttleEndTimeMillis:Date.now()},o=new Gn;return setTimeout(async()=>{o.abort()},yn),ut({appId:n,apiKey:s,measurementId:r},i,o,t)}async function ut(e,{throttleEndTimeMillis:t,backoffCount:a},n,s=lt){var r;const{appId:i,measurementId:o}=e;try{await Un(n,t)}catch(c){if(o)return p.warn(`Timed out fetching this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${c==null?void 0:c.message}]`),{appId:i,measurementId:o};throw c}try{const c=await xn(e);return s.deleteThrottleMetadata(i),c}catch(c){const l=c;if(!jn(l)){if(s.deleteThrottleMetadata(i),o)return p.warn(`Failed to fetch this Firebase app's measurement ID from the server. Falling back to the measurement ID ${o} provided in the "measurementId" field in the local Firebase config. [${l==null?void 0:l.message}]`),{appId:i,measurementId:o};throw c}const h=Number((r=l==null?void 0:l.customData)===null||r===void 0?void 0:r.httpStatus)===503?Y(a,s.intervalMillis,Bn):Y(a,s.intervalMillis),d={throttleEndTimeMillis:Date.now()+h,backoffCount:a+1};return s.setThrottleMetadata(i,d),p.debug(`Calling attemptFetch again in ${h} millis`),ut(e,d,n,s)}}function Un(e,t){return new Promise((a,n)=>{const s=Math.max(t-Date.now(),0),r=setTimeout(a,s);e.addEventListener(()=>{clearTimeout(r),n(C.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function jn(e){if(!(e instanceof D)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class Gn{constructor(){this.listeners=[]}addEventListener(t){this.listeners.push(t)}abort(){this.listeners.forEach(t=>t())}}async function Wn(e,t,a,n,s){if(s&&s.global){e("event",a,n);return}else{const r=await t,i=Object.assign(Object.assign({},n),{send_to:r});e("event",a,i)}}/**
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
 */async function qn(){if(ee())try{await ve()}catch(e){return p.warn(C.create("indexeddb-unavailable",{errorInfo:e==null?void 0:e.toString()}).message),!1}else return p.warn(C.create("indexeddb-unavailable",{errorInfo:"IndexedDB is not available in this environment."}).message),!1;return!0}async function zn(e,t,a,n,s,r,i){var o;const c=Vn(e);c.then(g=>{a[g.measurementId]=g.appId,e.options.measurementId&&g.measurementId!==e.options.measurementId&&p.warn(`The measurement ID in the local Firebase config (${e.options.measurementId}) does not match the measurement ID fetched from the server (${g.measurementId}). To ensure analytics events are always sent to the correct Analytics property, update the measurement ID field in the local config or remove it from the local config.`)}).catch(g=>p.error(g)),t.push(c);const l=qn().then(g=>{if(g)return n.getId()}),[h,d]=await Promise.all([c,l]);vn(r)||Rn(r,h.measurementId),s("js",new Date);const f=(o=i==null?void 0:i.config)!==null&&o!==void 0?o:{};return f[Tn]="firebase",f.update=!0,d!=null&&(f[wn]=d),s("config",h.measurementId,f),h.measurementId}/**
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
 */class Yn{constructor(t){this.app=t}_delete(){return delete k[this.app.options.appId],Promise.resolve()}}let k={},Se=[];const we={};let q="dataLayer",Xn="gtag",Te,dt,ye=!1;function Jn(){const e=[];if(Tt()&&e.push("This is a browser extension environment."),yt()||e.push("Cookies are not available."),e.length>0){const t=e.map((n,s)=>`(${s+1}) ${n}`).join(" "),a=C.create("invalid-analytics-context",{errorInfo:t});p.warn(a.message)}}function Qn(e,t,a){Jn();const n=e.options.appId;if(!n)throw C.create("no-app-id");if(!e.options.apiKey)if(e.options.measurementId)p.warn(`The "apiKey" field is empty in the local Firebase config. This is needed to fetch the latest measurement ID for this Firebase app. Falling back to the measurement ID ${e.options.measurementId} provided in the "measurementId" field in the local Firebase config.`);else throw C.create("no-api-key");if(k[n]!=null)throw C.create("already-exists",{id:n});if(!ye){Fn(q);const{wrappedGtag:r,gtagCore:i}=Nn(k,Se,we,q,Xn);dt=r,Te=i,ye=!0}return k[n]=zn(e,Se,we,t,Te,q,a),new Yn(e)}function Zn(e,t,a,n){e=Be(e),Wn(dt,k[e.app.options.appId],t,a,n).catch(s=>p.error(s))}const Ae="@firebase/analytics",De="0.10.12";function es(){A(new y(be,(t,{options:a})=>{const n=t.getProvider("app").getImmediate(),s=t.getProvider("installations-internal").getImmediate();return Qn(n,s,a)},"PUBLIC")),A(new y("analytics-internal",e,"PRIVATE")),E(Ae,De),E(Ae,De,"esm2017");function e(t){try{const a=t.getProvider(be).getImmediate();return{logEvent:(n,s,r)=>Zn(a,n,s,r)}}catch(a){throw C.create("interop-component-reg-failed",{reason:a})}}}es();const z="@firebase/remote-config",Oe="0.6.0";/**
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
 */const ts="remote-config",Le=100;/**
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
 */const as={"already-initialized":"Remote Config already initialized","registration-window":"Undefined window object. This SDK only supports usage in a browser environment.","registration-project-id":"Undefined project identifier. Check Firebase app initialization.","registration-api-key":"Undefined API key. Check Firebase app initialization.","registration-app-id":"Undefined app identifier. Check Firebase app initialization.","storage-open":"Error thrown when opening storage. Original error: {$originalErrorMessage}.","storage-get":"Error thrown when reading from storage. Original error: {$originalErrorMessage}.","storage-set":"Error thrown when writing to storage. Original error: {$originalErrorMessage}.","storage-delete":"Error thrown when deleting from storage. Original error: {$originalErrorMessage}.","fetch-client-network":"Fetch client failed to connect to a network. Check Internet connection. Original error: {$originalErrorMessage}.","fetch-timeout":'The config fetch request timed out.  Configure timeout using "fetchTimeoutMillis" SDK setting.',"fetch-throttle":'The config fetch request timed out while in an exponential backoff state. Configure timeout using "fetchTimeoutMillis" SDK setting. Unix timestamp in milliseconds when fetch request throttling ends: {$throttleEndTimeMillis}.',"fetch-client-parse":"Fetch client could not parse response. Original error: {$originalErrorMessage}.","fetch-status":"Fetch server returned an HTTP error status. HTTP status: {$httpStatus}.","indexed-db-unavailable":"Indexed DB is not supported by current browser","custom-signal-max-allowed-signals":"Setting more than {$maxSignals} custom signals is not supported."},m=new N("remoteconfig","Remote Config",as);function ns(e){const t=Be(e);return t._initializePromise||(t._initializePromise=t._storageCache.loadFromStorage().then(()=>{t._isInitializationComplete=!0})),t._initializePromise}/**
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
 */class ss{constructor(t,a,n,s){this.client=t,this.storage=a,this.storageCache=n,this.logger=s}isCachedDataFresh(t,a){if(!a)return this.logger.debug("Config fetch cache check. Cache unpopulated."),!1;const n=Date.now()-a,s=n<=t;return this.logger.debug(`Config fetch cache check. Cache age millis: ${n}. Cache max age millis (minimumFetchIntervalMillis setting): ${t}. Is cache hit: ${s}.`),s}async fetch(t){const[a,n]=await Promise.all([this.storage.getLastSuccessfulFetchTimestampMillis(),this.storage.getLastSuccessfulFetchResponse()]);if(n&&this.isCachedDataFresh(t.cacheMaxAgeMillis,a))return n;t.eTag=n&&n.eTag;const s=await this.client.fetch(t),r=[this.storageCache.setLastSuccessfulFetchTimestampMillis(Date.now())];return s.status===200&&r.push(this.storage.setLastSuccessfulFetchResponse(s)),await Promise.all(r),s}}/**
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
 */function rs(e=navigator){return e.languages&&e.languages[0]||e.language}/**
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
 */class is{constructor(t,a,n,s,r,i){this.firebaseInstallations=t,this.sdkVersion=a,this.namespace=n,this.projectId=s,this.apiKey=r,this.appId=i}async fetch(t){const[a,n]=await Promise.all([this.firebaseInstallations.getId(),this.firebaseInstallations.getToken()]),r=`${window.FIREBASE_REMOTE_CONFIG_URL_BASE||"https://firebaseremoteconfig.googleapis.com"}/v1/projects/${this.projectId}/namespaces/${this.namespace}:fetch?key=${this.apiKey}`,i={"Content-Type":"application/json","Content-Encoding":"gzip","If-None-Match":t.eTag||"*"},o={sdk_version:this.sdkVersion,app_instance_id:a,app_instance_id_token:n,app_id:this.appId,language_code:rs(),custom_signals:t.customSignals},c={method:"POST",headers:i,body:JSON.stringify(o)},l=fetch(r,c),h=new Promise((_,S)=>{t.signal.addEventListener(()=>{const le=new Error("The operation was aborted.");le.name="AbortError",S(le)})});let d;try{await Promise.race([l,h]),d=await l}catch(_){let S="fetch-client-network";throw(_==null?void 0:_.name)==="AbortError"&&(S="fetch-timeout"),m.create(S,{originalErrorMessage:_==null?void 0:_.message})}let f=d.status;const g=d.headers.get("ETag")||void 0;let O,b;if(d.status===200){let _;try{_=await d.json()}catch(S){throw m.create("fetch-client-parse",{originalErrorMessage:S==null?void 0:S.message})}O=_.entries,b=_.state}if(b==="INSTANCE_STATE_UNSPECIFIED"?f=500:b==="NO_CHANGE"?f=304:(b==="NO_TEMPLATE"||b==="EMPTY_CONFIG")&&(O={}),f!==304&&f!==200)throw m.create("fetch-status",{httpStatus:f});return{status:f,eTag:g,config:O}}}/**
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
 */function os(e,t){return new Promise((a,n)=>{const s=Math.max(t-Date.now(),0),r=setTimeout(a,s);e.addEventListener(()=>{clearTimeout(r),n(m.create("fetch-throttle",{throttleEndTimeMillis:t}))})})}function cs(e){if(!(e instanceof D)||!e.customData)return!1;const t=Number(e.customData.httpStatus);return t===429||t===500||t===503||t===504}class ls{constructor(t,a){this.client=t,this.storage=a}async fetch(t){const a=await this.storage.getThrottleMetadata()||{backoffCount:0,throttleEndTimeMillis:Date.now()};return this.attemptFetch(t,a)}async attemptFetch(t,{throttleEndTimeMillis:a,backoffCount:n}){await os(t.signal,a);try{const s=await this.client.fetch(t);return await this.storage.deleteThrottleMetadata(),s}catch(s){if(!cs(s))throw s;const r={throttleEndTimeMillis:Date.now()+Y(n),backoffCount:n+1};return await this.storage.setThrottleMetadata(r),this.attemptFetch(t,r)}}}/**
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
 */const us=60*1e3,ds=12*60*60*1e3;class hs{get fetchTimeMillis(){return this._storageCache.getLastSuccessfulFetchTimestampMillis()||-1}get lastFetchStatus(){return this._storageCache.getLastFetchStatus()||"no-fetch-yet"}constructor(t,a,n,s,r){this.app=t,this._client=a,this._storageCache=n,this._storage=s,this._logger=r,this._isInitializationComplete=!1,this.settings={fetchTimeoutMillis:us,minimumFetchIntervalMillis:ds},this.defaultConfig={}}}/**
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
 */function B(e,t){const a=e.target.error||void 0;return m.create(t,{originalErrorMessage:a&&(a==null?void 0:a.message)})}const w="app_namespace_store",fs="firebase_remote_config",gs=1;function ps(){return new Promise((e,t)=>{try{const a=indexedDB.open(fs,gs);a.onerror=n=>{t(B(n,"storage-open"))},a.onsuccess=n=>{e(n.target.result)},a.onupgradeneeded=n=>{const s=n.target.result;switch(n.oldVersion){case 0:s.createObjectStore(w,{keyPath:"compositeKey"})}}}catch(a){t(m.create("storage-open",{originalErrorMessage:a==null?void 0:a.message}))}})}class ht{getLastFetchStatus(){return this.get("last_fetch_status")}setLastFetchStatus(t){return this.set("last_fetch_status",t)}getLastSuccessfulFetchTimestampMillis(){return this.get("last_successful_fetch_timestamp_millis")}setLastSuccessfulFetchTimestampMillis(t){return this.set("last_successful_fetch_timestamp_millis",t)}getLastSuccessfulFetchResponse(){return this.get("last_successful_fetch_response")}setLastSuccessfulFetchResponse(t){return this.set("last_successful_fetch_response",t)}getActiveConfig(){return this.get("active_config")}setActiveConfig(t){return this.set("active_config",t)}getActiveConfigEtag(){return this.get("active_config_etag")}setActiveConfigEtag(t){return this.set("active_config_etag",t)}getThrottleMetadata(){return this.get("throttle_metadata")}setThrottleMetadata(t){return this.set("throttle_metadata",t)}deleteThrottleMetadata(){return this.delete("throttle_metadata")}getCustomSignals(){return this.get("custom_signals")}}class ms extends ht{constructor(t,a,n,s=ps()){super(),this.appId=t,this.appName=a,this.namespace=n,this.openDbPromise=s}async setCustomSignals(t){const n=(await this.openDbPromise).transaction([w],"readwrite"),s=await this.getWithTransaction("custom_signals",n),r=ft(t,s||{});return await this.setWithTransaction("custom_signals",r,n),r}async getWithTransaction(t,a){return new Promise((n,s)=>{const r=a.objectStore(w),i=this.createCompositeKey(t);try{const o=r.get(i);o.onerror=c=>{s(B(c,"storage-get"))},o.onsuccess=c=>{const l=c.target.result;n(l?l.value:void 0)}}catch(o){s(m.create("storage-get",{originalErrorMessage:o==null?void 0:o.message}))}})}async setWithTransaction(t,a,n){return new Promise((s,r)=>{const i=n.objectStore(w),o=this.createCompositeKey(t);try{const c=i.put({compositeKey:o,value:a});c.onerror=l=>{r(B(l,"storage-set"))},c.onsuccess=()=>{s()}}catch(c){r(m.create("storage-set",{originalErrorMessage:c==null?void 0:c.message}))}})}async get(t){const n=(await this.openDbPromise).transaction([w],"readonly");return this.getWithTransaction(t,n)}async set(t,a){const s=(await this.openDbPromise).transaction([w],"readwrite");return this.setWithTransaction(t,a,s)}async delete(t){const a=await this.openDbPromise;return new Promise((n,s)=>{const i=a.transaction([w],"readwrite").objectStore(w),o=this.createCompositeKey(t);try{const c=i.delete(o);c.onerror=l=>{s(B(l,"storage-delete"))},c.onsuccess=()=>{n()}}catch(c){s(m.create("storage-delete",{originalErrorMessage:c==null?void 0:c.message}))}})}createCompositeKey(t){return[this.appId,this.appName,this.namespace,t].join()}}class Cs extends ht{constructor(){super(...arguments),this.storage={}}async get(t){return Promise.resolve(this.storage[t])}async set(t,a){return this.storage[t]=a,Promise.resolve(void 0)}async delete(t){return this.storage[t]=void 0,Promise.resolve()}async setCustomSignals(t){const a=this.storage.custom_signals||{};return this.storage.custom_signals=ft(t,a),Promise.resolve(this.storage.custom_signals)}}function ft(e,t){const a=Object.assign(Object.assign({},t),e),n=Object.fromEntries(Object.entries(a).filter(([s,r])=>r!==null).map(([s,r])=>typeof r=="number"?[s,r.toString()]:[s,r]));if(Object.keys(n).length>Le)throw m.create("custom-signal-max-allowed-signals",{maxSignals:Le});return n}/**
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
 */class _s{constructor(t){this.storage=t}getLastFetchStatus(){return this.lastFetchStatus}getLastSuccessfulFetchTimestampMillis(){return this.lastSuccessfulFetchTimestampMillis}getActiveConfig(){return this.activeConfig}getCustomSignals(){return this.customSignals}async loadFromStorage(){const t=this.storage.getLastFetchStatus(),a=this.storage.getLastSuccessfulFetchTimestampMillis(),n=this.storage.getActiveConfig(),s=this.storage.getCustomSignals(),r=await t;r&&(this.lastFetchStatus=r);const i=await a;i&&(this.lastSuccessfulFetchTimestampMillis=i);const o=await n;o&&(this.activeConfig=o);const c=await s;c&&(this.customSignals=c)}setLastFetchStatus(t){return this.lastFetchStatus=t,this.storage.setLastFetchStatus(t)}setLastSuccessfulFetchTimestampMillis(t){return this.lastSuccessfulFetchTimestampMillis=t,this.storage.setLastSuccessfulFetchTimestampMillis(t)}setActiveConfig(t){return this.activeConfig=t,this.storage.setActiveConfig(t)}async setCustomSignals(t){this.customSignals=await this.storage.setCustomSignals(t)}}/**
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
 */function Es(){A(new y(ts,e,"PUBLIC").setMultipleInstances(!0)),E(z,Oe),E(z,Oe,"esm2017");function e(t,{options:a}){const n=t.getProvider("app").getImmediate(),s=t.getProvider("installations-internal").getImmediate(),{projectId:r,apiKey:i,appId:o}=n.options;if(!r)throw m.create("registration-project-id");if(!i)throw m.create("registration-api-key");if(!o)throw m.create("registration-app-id");const c=(a==null?void 0:a.templateId)||"firebase",l=ee()?new ms(o,n.name,c):new Cs,h=new _s(l),d=new te(z);d.logLevel=u.ERROR;const f=new is(s,Aa,c,r,i,o),g=new ls(f,l),O=new ss(g,l,h,d),b=new hs(n,O,h,l,d);return ns(b),b}}Es();const Is=e=>Object.fromEntries(new URLSearchParams(e)),bs=()=>{const e=Ct(),t=Is(e.search);return"utm_campaign"in t&&"utm_medium"in t&&"utm_source"in t?{traffic_campaign:t.utm_campaign,traffic_medium:t.utm_medium,traffic_source:t.utm_source}:{}},Ss=()=>{const e=bs();return{logEvent:mt.useCallback((a,n)=>{},[e])}};var gt=(e=>(e.CLICKED_BOOKING="hasClickedBooking",e.CLICKED_CANCELED_SELECTED_OFFERS="hasClickedCancelOffers",e.CLICKED_DISABLED_SELECTED_OFFERS="hasClickedDisabledOffers",e.CLICKED_CONSULT_CGU="hasClickedConsultCGU",e.CLICKED_CONSULT_SUPPORT="hasClickedConsultSupport",e.CLICKED_CREATE_ACCOUNT="hasClickedCreateAccount",e.CLICKED_CREATE_VENUE="hasClickedCreateVenue",e.CLICKED_SEE_LATER_FROM_SUCCESS_VENUE_CREATION_MODAL="hasClickedSeeLaterFromSuccessVenueCreationModal",e.CLICKED_SEE_LATER_FROM_SUCCESS_OFFER_CREATION_MODAL="hasClickedSeeLaterFromSuccessOfferCreationModal",e.CLICKED_SAVE_VENUE="hasClickedSaveVenue",e.CLICKED_DOWNLOAD_BOOKINGS="hasClickedDownloadBooking",e.CLICKED_DOWNLOAD_BOOKINGS_CSV="hasClickedDownloadBookingCsv",e.CLICKED_DOWNLOAD_BOOKINGS_XLS="hasClickedDownloadBookingXls",e.CLICKED_EDIT_PROFILE="hasClickedEditProfile",e.CLICKED_EDIT_COLLECTIVE_OFFER="hasClickedEditCollectiveOffer",e.CLICKED_HOME_STATS_PENDING_OFFERS_FAQ="hasClickedHomeStatsPendingOffersFaq",e.CLICKED_FORGOTTEN_PASSWORD="hasClickedForgottenPassword",e.CLICKED_HELP_CENTER="hasClickedHelpCenter",e.CLICKED_HOME="hasClickedHome",e.CLICKED_LOGOUT="hasClickedLogout",e.CLICKED_CONFIRMED_ADD_HEADLINE_OFFER="hasClickedConfirmedAddHeadlineOffer",e.CLICKED_DISCOVERED_HEADLINE_OFFER="hasClickedDiscoveredHeadlineOffer",e.CLICKED_OFFER="hasClickedOffer",e.CLICKED_OFFER_FORM_NAVIGATION="hasClickedOfferFormNavigation",e.CLICKED_ONBOARDING_FORM_NAVIGATION="HasClickedOnboardingFormNavigation",e.CLICKED_CANCEL_OFFER_CREATION="hasClickedCancelOfferCreation",e.CLICKED_PARTNER_BLOCK_PREVIEW_VENUE_LINK="hasClickedPartnerBlockPreviewVenueLink",e.CLICKED_PARTNER_BLOCK_COPY_VENUE_LINK="hasClickedPartnerBlockCopyVenueLink",e.CLICKED_PARTNER_BLOCK_DMS_APPLICATION_LINK="hasClickedPartnerBlockDmsApplicationLink",e.CLICKED_PARTNER_BLOCK_COLLECTIVE_HELP_LINK="hasClickedPartnerBlockCollectiveHelpLink",e.CLICKED_PERSONAL_DATA="hasClickedConsultPersonalData",e.CLICKED_PRO="hasClickedPro",e.CLICKED_REIMBURSEMENT="hasClickedReimbursement",e.CLICKED_SHOW_BOOKINGS="hasClickedShowBooking",e.CLICKED_STATS="hasClickedOffererStats",e.CLICKED_TICKET="hasClickedTicket",e.CLICKED_DUPLICATE_TEMPLATE_OFFER="hasClickedDuplicateTemplateOffer",e.CLICKED_DUPLICATE_BOOKABLE_OFFER="hasClickedDuplicateBookableOffer",e.CLICKED_BEST_PRACTICES_STUDIES="hasClickedBestPracticesAndStudies",e.CLICKED_HELP_LINK="hasClickedHelpLink",e.CLICKED_RESET_FILTERS="hasClickedResetFilter",e.CLICKED_SHOW_STATUS_FILTER="hasClickedShowStatusFilter",e.CLICKED_OMNI_SEARCH_CRITERIA="hasClickedOmniSearchCriteria",e.CLICKED_PAGINATION_NEXT_PAGE="hasClickedPaginationNextPage",e.CLICKED_PAGINATION_PREVIOUS_PAGE="hasClickedPaginationPreviousPage",e.CLICKED_CONTACT_OUR_TEAMS="hasClickedContactOurTeams",e.CLICKED_ARCHIVE_COLLECTIVE_OFFER="hasClickedArchiveCollectiveOffer",e.CLICKED_SAVE_DRAFT_AND_EXIT_COLLECTIVE_OFFER="hasClickedSaveDraftAndExitCollectiveOffer",e.CLICKED_SEE_TEMPLATE_OFFER_EXAMPLE="hasClickedSeeTemplateOfferExample",e.FIRST_LOGIN="firstLogin",e.PAGE_VIEW="page_view",e.SIGNUP_FORM_ABORT="signupFormAbort",e.SIGNUP_FORM_SUCCESS="signupFormSuccess",e.TUTO_PAGE_VIEW="tutoPageView",e.DELETE_DRAFT_OFFER="DeleteDraftOffer",e.CLICKED_NO_VENUE="hasClickedNoVenue",e.CLICKED_EAC_DMS_TIMELINE="hasClickedEacDmsTimeline",e.CLICKED_EAC_DMS_LINK="hasClickedEacDmsLink",e.CLICKED_CREATE_OFFER_FROM_REQUEST="hasClickedCreateOfferFromRequest",e.CLICKED_ADD_IMAGE="hasClickedAddImage",e.CLICKED_DELETE_STOCK="hasClickedDeleteStock",e.CLICKED_BULK_DELETE_STOCK="hasClickedBulkDeleteStock",e.CLICKED_DOWNLOAD_OFFER_BOOKINGS="hasDownloadedBookings",e.CLICKED_PAGE_FOR_APP_HOME="hasClickedPageForAppHome",e.CLICKED_PAGE_FOR_ADAGE_HOME="hasClickedPageForAdageHome",e.CLICKED_INVOICES_DOWNLOAD="hasClickedInvoicesDownload",e.CLICKED_PUBLISH_FUTURE_OFFER_EARLIER="hasClickedPublishFutureOfferEarlier",e.EXTRA_PRO_DATA="extra_pro_data",e.CLICKED_NEW_EVOLUTIONS="hasClickedNewEvolutions",e.CLICKED_CONSULT_HELP="hasClickedConsultHelp",e.UPDATED_BOOKING_LIMIT_DATE="hasUpdatedBookingLimitDate",e.CLICKED_GENERATE_TEMPLATE_DESCRIPTION="hasClickedGenerateTemplateDescription",e.UPDATED_EVENT_STOCK_FILTERS="hasUpdatedEventStockFilters",e.CLICKED_VALIDATE_ADD_RECURRENCE_DATES="hasClickedValidateAddRecurrenceDates",e.FAKE_DOOR_VIDEO_INTERESTED="fakeDoorVideoInterested",e.CLICKED_SORT_STOCKS_TABLE="hasClickedSortStocksTable",e))(gt||{});const Re={"help-link":"_help-link_1jav9_1","help-link-text":"_help-link-text_1jav9_9"},ws=()=>{const{logEvent:e}=Ss();return P.jsxs("a",{onClick:()=>e(gt.CLICKED_HELP_LINK,{from:location.pathname}),className:Re["help-link"],href:"https://aide.passculture.app/hc/fr/articles/4411991940369--Acteurs-culturels-Comment-poster-une-offre-%C3%A0-destination-d-un-groupe-scolaire-",rel:"noreferrer",target:"_blank",children:[P.jsx(Et,{src:_t,alt:"",width:"42"}),P.jsx("span",{className:Re["help-link-text"],children:"Aide"})]})},ks={title:"components/HelpLink",component:ws,decorators:[e=>P.jsx("div",{style:{width:500,height:500},children:P.jsx(e,{})}),pt]},v={};var Fe,Pe,ke;v.parameters={...v.parameters,docs:{...(Fe=v.parameters)==null?void 0:Fe.docs,source:{originalSource:"{}",...(ke=(Pe=v.parameters)==null?void 0:Pe.docs)==null?void 0:ke.source}}};const Ms=["Default"];export{v as Default,Ms as __namedExportsOrder,ks as default};
