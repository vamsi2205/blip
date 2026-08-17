# Blip — desk companion prototype

## What's here
- `index.html` — the whole app: animated blob face, tap-to-talk mic (Web Speech API), Gemini call, text bubble, settings modal.
- `manifest.json` + `sw.js` + `icon.svg` — makes it installable as a PWA (Add to Home Screen, fullscreen, works offline for the shell).

## Important: I can't compile a real .apk file in this sandbox
Building a signed APK needs the Android SDK/Gradle toolchain, which isn't available in this environment (no network access to Google's Maven repos, no emulator to test on). What I *can* build — and did — is a fully working web app. Turning it into an actual APK from here takes one extra step on your end, and there are two easy paths:

### Path A — PWABuilder (no coding, ~10 minutes)
1. Deploy this folder somewhere with HTTPS. Easiest: push it to a GitHub repo and enable GitHub Pages (same pattern as your other projects) — you'll get a URL like `https://yourname.github.io/blip/`.
2. Go to **pwabuilder.com**, paste that URL.
3. It scores your manifest, then lets you download an **Android package (APK or AAB)** directly — no Android Studio needed.
4. Sideload the APK onto the old phone (enable "install unknown apps" for your browser/file manager), or install straight from the PWABuilder-hosted link.

### Path B — Capacitor (more control, needs Android Studio)
1. `npm install @capacitor/core @capacitor/android`
2. `npx cap init blip com.vamsi.blip`
3. Copy `index.html`, `manifest.json`, `sw.js`, `icon.svg` into the Capacitor `www/` folder.
4. `npx cap add android` then `npx cap open android` — builds and signs the APK in Android Studio, installs straight to a plugged-in phone over USB.

Either path gets you a real app icon on the home screen, no browser chrome, and (with Capacitor) access to more native APIs later if you want always-on wake word detection or background listening.

## Before you deploy
- Get a free Gemini API key from **aistudio.google.com/apikey**.
- Open the app, tap the gear icon, paste the key in. It's kept in memory only for that session (see the comment block in `index.html`'s script for how to persist it with `localStorage` once this is running on its own domain).
- Tweak the "Personality" text in settings — that's the system instruction that shapes Blip's voice/tone.

## What changed in this version
- Idle screen shows only the blob and a small greeting + clock — no mic/settings clutter.
- The blob now cycles ambient moods (curious, sleepy, content, alert) on its own while idle, like the MSG sphere.
- Mic and settings live in a slide-out drawer behind the translucent arrow tab on the right edge.
- Say "hey blip" and it starts listening automatically (needs the always-listen toggle on in settings); tapping the mic in the drawer still works as manual tap-to-talk.
- After a reply, Blip stays in the "active" view (bubble + status) for about 6 seconds, then fades back to the idle clock view — it won't jump to something else until you ask it to.
- If you ask Blip to open or show something, the reply can include a tappable "open it" link instead of auto-navigating — see the note below on why it's tap-to-open rather than automatic.

## Real limits worth knowing about
- **Wake phrase only works while the screen is on and the tab is active.** Browsers freeze all JavaScript, including the mic, the instant the screen sleeps or the app backgrounds — this is a deliberate OS/browser protection, not a bug I can code around. Since this is a desk gadget, the practical fix is: set the phone to never sleep while charging, and let Blip's wake-lock keep the display on. True screen-off wake-word detection needs a native Android background service (Capacitor + a wake-word engine like Picovoice) — a bigger separate build if you want it later.
- **Opening links is tap-to-confirm, not automatic.** Two reasons: Chrome's popup blocker silently kills `window.open()` calls that don't happen from a direct tap (a voice reply arrives asynchronously, so it gets blocked), and it's generally safer for something to ask before jumping to another app or site rather than doing it silently.
- **Orientation lock and fullscreen need that first tap** on the wake screen — Android requires a real user gesture before granting those, so there's no way to skip straight to fullscreen landscape on load.

## Known rough edges (it's a prototype)
- Mouth movement during speech is a simple pulse, not real lip-sync.
- `SpeechRecognition` is tap-to-talk, not always-listening — true wake-word detection needs a native (Capacitor) build with background mic access, which browsers restrict.
- Voice quality depends on the phone's built-in TTS voices; you can swap in Gemini's own TTS or ElevenLabs later for something nicer.
- Old Android + old WebView can be flaky with the Web Speech API — if voice input doesn't work, check that the browser is a recent Chrome (WebView version matters more than Android version).
